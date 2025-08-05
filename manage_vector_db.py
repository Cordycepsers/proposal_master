#!/usr/bin/env python3
"""
Vector Database Management CLI

This script provides command-line utilities for managing the vector database,
including indexing, searching, and maintenance operations.
"""

import asyncio
import click
import logging
import json
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import time
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.vector_database import VectorDatabase, VectorDocument, VectorIndexConfig
from src.services.vector_integration import create_vector_integration_service
from src.config.vector_config import (
    get_vector_config, validate_vector_config, 
    get_recommended_config, get_embedding_model_info
)
from src.config.database import get_db
from src.models.core import TenderOpportunity, Proposal, WonBid, ProjectDocumentation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_vector_db() -> VectorDatabase:
    """Get vector database instance"""
    try:
        config = get_vector_config()
        
        # Convert VectorConfig to VectorIndexConfig
        index_config = VectorIndexConfig(
            dimension=config.dimension,
            index_type=config.index_type,
            metric=config.metric,
            nlist=config.nlist,
            nprobe=config.nprobe,
            store_on_disk=config.store_on_disk,
            index_path=config.index_path,
            metadata_path=config.metadata_path,
            embedding_model=config.embedding_model,
            batch_size=config.batch_size,
            max_retries=config.max_retries
        )
        
        return VectorDatabase(index_config)
    except Exception as e:
        logger.error(f"Error creating vector database: {e}")
        raise

@click.group()
def cli():
    """Vector Database Management CLI"""
    pass

@cli.command()
@click.option('--use-case', default='general', 
              type=click.Choice(['general', 'high_quality', 'large_scale', 'openai', 'multilingual', 'qa_optimized']),
              help='Use case for recommended configuration')
@click.option('--model', help='Embedding model to use')
@click.option('--index-type', help='FAISS index type')
@click.option('--validate', is_flag=True, help='Validate configuration')
def config(use_case: str, model: Optional[str], index_type: Optional[str], validate: bool):
    """Configure vector database settings"""
    
    if use_case != 'general':
        config_obj = get_recommended_config(use_case)
        click.echo(f"Recommended configuration for '{use_case}':")
    else:
        config_obj = get_vector_config()
        click.echo("Current configuration:")
    
    # Apply overrides
    if model:
        config_obj.embedding_model = model
    if index_type:
        config_obj.index_type = index_type
    
    # Display configuration
    click.echo(f"  Embedding Model: {config_obj.embedding_model}")
    click.echo(f"  Index Type: {config_obj.index_type}")
    click.echo(f"  Dimension: {config_obj.embedding_dimension}")
    click.echo(f"  Batch Size: {config_obj.batch_size}")
    click.echo(f"  Chunk Size: {config_obj.chunk_size}")
    click.echo(f"  Index Path: {config_obj.index_path}")
    
    # Show model information
    if model or use_case != 'general':
        model_info = get_embedding_model_info(config_obj.embedding_model)
        click.echo(f"\nModel Information:")
        click.echo(f"  Provider: {model_info.get('provider', 'unknown')}")
        click.echo(f"  Description: {model_info.get('description', 'N/A')}")
        click.echo(f"  Performance: {model_info.get('performance', 'unknown')}")
        click.echo(f"  Quality: {model_info.get('quality', 'unknown')}")
        if 'cost_per_1k_tokens' in model_info:
            click.echo(f"  Cost per 1K tokens: ${model_info['cost_per_1k_tokens']}")
    
    # Validate configuration
    if validate:
        validation = validate_vector_config(config_obj)
        click.echo(f"\nValidation Result: {'✅ VALID' if validation['valid'] else '❌ INVALID'}")
        
        if validation['issues']:
            click.echo("Issues:")
            for issue in validation['issues']:
                click.echo(f"  ❌ {issue}")
        
        if validation['warnings']:
            click.echo("Warnings:")
            for warning in validation['warnings']:
                click.echo(f"  ⚠️  {warning}")

@cli.command()
@click.option('--embedding-model', default='all-MiniLM-L6-v2', help='Embedding model to use')
@click.option('--index-path', help='Path to store the index')
@click.option('--index-type', default='IndexFlatIP', help='FAISS index type')
def init(embedding_model: str, index_path: Optional[str], index_type: str):
    """Initialize a new vector database"""
    try:
        # Get base configuration
        config = get_vector_config()
        
        # Override with command line parameters
        if index_path:
            config.index_path = index_path
            config.metadata_path = index_path.replace('.faiss', '_metadata.json')
        
        config.embedding_model = embedding_model
        config.index_type = index_type
        
        # Convert VectorConfig to VectorIndexConfig  
        index_config = VectorIndexConfig(
            dimension=config.dimension,
            index_type=config.index_type,
            metric=config.metric,
            nlist=config.nlist,
            nprobe=config.nprobe,
            store_on_disk=config.store_on_disk,
            index_path=config.index_path,
            metadata_path=config.metadata_path,
            embedding_model=config.embedding_model,
            batch_size=config.batch_size,
            max_retries=config.max_retries
        )
        
        # Create vector database
        vector_db = VectorDatabase(index_config)
        
        stats = vector_db.get_stats()
        click.echo("Vector database initialized successfully!")
        click.echo(f"  Model: {stats['embedding_model']}")
        click.echo(f"  Dimension: {stats['dimension']}")
        click.echo(f"  Index Type: {stats['index_type']}")
        click.echo(f"  Documents: {stats['total_documents']}")
        
    except Exception as e:
        click.echo(f"Failed to initialize vector database: {e}", err=True)
        sys.exit(1)

@cli.command()
def stats():
    """Show vector database statistics"""
    try:
        vector_service = create_vector_integration_service()
        stats = vector_service.vector_db.get_stats()
        
        click.echo("Vector Database Statistics:")
        click.echo(f"  Total Documents: {stats['total_documents']:,}")
        click.echo(f"  Total Vectors: {stats['total_vectors']:,}")
        click.echo(f"  Dimension: {stats['dimension']}")
        click.echo(f"  Index Type: {stats['index_type']}")
        click.echo(f"  Embedding Model: {stats['embedding_model']}")
        click.echo(f"  Initialized: {'Yes' if stats['is_initialized'] else 'No'}")
        
    except Exception as e:
        click.echo(f"Failed to get statistics: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--batch-size', default=50, help='Batch size for processing')
@click.option('--type', 'content_type', type=click.Choice(['all', 'tenders', 'proposals', 'won_bids', 'project_docs']),
              default='all', help='Type of content to index')
def index(batch_size: int, content_type: str):
    """Index all documents in the database"""
    
    async def do_index():
        try:
            vector_service = create_vector_integration_service()
            
            click.echo(f"Starting bulk indexing (batch size: {batch_size})")
            start_time = time.time()
            
            if content_type == 'all':
                await vector_service.bulk_reindex(batch_size)
            else:
                # Index specific content type
                async with get_db() as db:
                    if content_type == 'tenders':
                        from sqlalchemy import select
                        from sqlalchemy.orm import selectinload
                        
                        stmt = select(TenderOpportunity).options(
                            selectinload(TenderOpportunity.requirements)
                        )
                        result = await db.execute(stmt)
                        items = result.scalars().all()
                        
                        for i, item in enumerate(items):
                            await vector_service.index_tender_opportunity(item)
                            if (i + 1) % batch_size == 0:
                                click.echo(f"Indexed {i + 1}/{len(items)} tenders")
                    
                    elif content_type == 'proposals':
                        from sqlalchemy import select
                        stmt = select(Proposal)
                        result = await db.execute(stmt)
                        items = result.scalars().all()
                        
                        for i, item in enumerate(items):
                            await vector_service.index_proposal(item)
                            if (i + 1) % batch_size == 0:
                                click.echo(f"Indexed {i + 1}/{len(items)} proposals")
                    
                    elif content_type == 'won_bids':
                        from sqlalchemy import select
                        stmt = select(WonBid)
                        result = await db.execute(stmt)
                        items = result.scalars().all()
                        
                        for i, item in enumerate(items):
                            await vector_service.index_won_bid(item)
                            if (i + 1) % batch_size == 0:
                                click.echo(f"Indexed {i + 1}/{len(items)} won bids")
                    
                    elif content_type == 'project_docs':
                        from sqlalchemy import select
                        stmt = select(ProjectDocumentation)
                        result = await db.execute(stmt)
                        items = result.scalars().all()
                        
                        for i, item in enumerate(items):
                            await vector_service.index_project_documentation(item)
                            if (i + 1) % batch_size == 0:
                                click.echo(f"Indexed {i + 1}/{len(items)} project docs")
            
            elapsed = time.time() - start_time
            click.echo(f"Indexing completed in {elapsed:.2f} seconds")
            
            # Show final stats
            stats = vector_service.vector_db.get_stats()
            click.echo(f"Total indexed documents: {stats['total_documents']:,}")
            
        except Exception as e:
            click.echo(f"Indexing failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(do_index())

@cli.command()
@click.argument('query')
@click.option('--top-k', default=10, help='Number of results to return')
@click.option('--type', 'search_type', type=click.Choice(['all', 'tenders', 'won_bids', 'project_docs']),
              default='all', help='Type of content to search')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'detailed']),
              default='table', help='Output format')
def search(query: str, top_k: int, search_type: str, output_format: str):
    """Search the vector database"""
    
    async def do_search():
        try:
            vector_service = create_vector_integration_service()
            
            click.echo(f"Searching for: '{query}' (top {top_k} results)")
            start_time = time.time()
            
            if search_type == 'all':
                # Search all documents
                results = await vector_service.vector_db.search(query, top_k)
                search_results = [(r.document, r.similarity_score) for r in results]
            elif search_type == 'tenders':
                search_results = await vector_service.semantic_search_tenders(query, top_k)
            elif search_type == 'won_bids':
                search_results = await vector_service.find_similar_won_bids(query, top_k)
            elif search_type == 'project_docs':
                search_results = await vector_service.search_project_documentation(query, top_k)
            
            elapsed = time.time() - start_time
            
            if not search_results:
                click.echo("No results found.")
                return
            
            click.echo(f"Found {len(search_results)} results in {elapsed:.3f} seconds")
            click.echo()
            
            if output_format == 'json':
                results_data = []
                for item, score in search_results:
                    if hasattr(item, 'id'):
                        # Database object
                        result_data = {
                            'score': float(score),
                            'type': type(item).__name__,
                            'id': item.id,
                            'title': getattr(item, 'title', getattr(item, 'project_title', 'N/A'))
                        }
                    else:
                        # Vector document
                        result_data = {
                            'score': float(score),
                            'id': item.id,
                            'content_preview': item.content[:100] + '...' if len(item.content) > 100 else item.content,
                            'metadata': item.metadata
                        }
                    results_data.append(result_data)
                
                click.echo(json.dumps(results_data, indent=2))
            
            elif output_format == 'detailed':
                for i, (item, score) in enumerate(search_results, 1):
                    click.echo(f"Result {i} (Score: {score:.4f})")
                    if hasattr(item, 'id'):
                        # Database object
                        click.echo(f"  Type: {type(item).__name__}")
                        click.echo(f"  ID: {item.id}")
                        if hasattr(item, 'title'):
                            click.echo(f"  Title: {item.title}")
                        if hasattr(item, 'project_title'):
                            click.echo(f"  Project: {item.project_title}")
                        if hasattr(item, 'organization'):
                            click.echo(f"  Organization: {item.organization}")
                    else:
                        # Vector document
                        click.echo(f"  Document ID: {item.id}")
                        click.echo(f"  Content: {item.content[:200]}{'...' if len(item.content) > 200 else ''}")
                        if item.metadata:
                            click.echo(f"  Metadata: {item.metadata}")
                    click.echo()
            
            else:  # table format
                click.echo(f"{'Rank':<5} {'Score':<8} {'Type':<15} {'Title/Content':<50}")
                click.echo("-" * 80)
                
                for i, (item, score) in enumerate(search_results, 1):
                    if hasattr(item, 'id'):
                        # Database object
                        item_type = type(item).__name__
                        title = getattr(item, 'title', getattr(item, 'project_title', 'N/A'))
                        content = title[:47] + "..." if len(title) > 50 else title
                    else:
                        # Vector document
                        item_type = item.metadata.get('type', 'Document')
                        content = item.content[:47] + "..." if len(item.content) > 50 else item.content
                    
                    click.echo(f"{i:<5} {score:<8.4f} {item_type:<15} {content:<50}")
        
        except Exception as e:
            click.echo(f"Search failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(do_search())

@cli.command()
@click.argument('tender_id', type=int)
@click.option('--top-k', default=5, help='Number of similar items to analyze')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']),
              default='table', help='Output format')
def recommend(tender_id: int, top_k: int, output_format: str):
    """Get recommendations for a tender"""
    
    async def do_recommend():
        try:
            vector_service = create_vector_integration_service()
            
            click.echo(f"Generating recommendations for tender {tender_id}...")
            start_time = time.time()
            
            recommendations = await vector_service.get_recommendations_for_tender(
                tender_id, top_k
            )
            
            elapsed = time.time() - start_time
            click.echo(f"Analysis completed in {elapsed:.2f} seconds")
            click.echo()
            
            if output_format == 'json':
                click.echo(json.dumps(recommendations, indent=2, default=str))
            else:
                click.echo(f"Recommendations for Tender {tender_id}:")
                click.echo(f"Similar Won Bids Found: {recommendations['similar_won_bids']}")
                click.echo(f"Relevant Documents: {len(recommendations['relevant_documentation'])}")
                click.echo()
                
                if recommendations['recommendations']:
                    click.echo("Key Recommendations:")
                    for rec in recommendations['recommendations']:
                        click.echo(f"  • {rec}")
                    click.echo()
                
                if recommendations['winning_patterns']:
                    click.echo("Winning Patterns from Similar Projects:")
                    for pattern in recommendations['winning_patterns'][:3]:
                        click.echo(f"  Project: {pattern.get('project', 'N/A')}")
                        if pattern.get('factors'):
                            click.echo(f"  Key Factors: {list(pattern['factors'].keys())[:3]}")
                        click.echo(f"  Similarity Score: {pattern.get('score', 0):.4f}")
                        click.echo()
        
        except Exception as e:
            click.echo(f"Recommendation failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(do_recommend())

@cli.command()
def rebuild():
    """Rebuild the vector index"""
    
    async def do_rebuild():
        try:
            vector_service = create_vector_integration_service()
            
            click.echo("Rebuilding vector index...")
            start_time = time.time()
            
            await vector_service.vector_db.rebuild_index()
            
            elapsed = time.time() - start_time
            click.echo(f"Index rebuilt in {elapsed:.2f} seconds")
            
            # Show final stats
            stats = vector_service.vector_db.get_stats()
            click.echo(f"Total documents: {stats['total_documents']:,}")
            click.echo(f"Total vectors: {stats['total_vectors']:,}")
            
        except Exception as e:
            click.echo(f"Rebuild failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(do_rebuild())

@cli.command()
@click.argument('document_id')
def delete(document_id: str):
    """Delete a document from the vector database"""
    
    async def do_delete():
        try:
            vector_service = create_vector_integration_service()
            
            success = await vector_service.vector_db.delete_document(document_id)
            
            if success:
                click.echo(f"Document '{document_id}' deleted successfully")
            else:
                click.echo(f"Document '{document_id}' not found")
                sys.exit(1)
        
        except Exception as e:
            click.echo(f"Delete failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(do_delete())

@cli.command()
@click.option('--limit', default=50, help='Maximum number of documents to list')
@click.option('--offset', default=0, help='Number of documents to skip')
@click.option('--type', 'doc_type', help='Filter by document type')
@click.option('--source', help='Filter by document source')
def list_docs(limit: int, offset: int, doc_type: Optional[str], source: Optional[str]):
    """List documents in the vector database"""
    try:
        vector_service = create_vector_integration_service()
        
        # Build filters
        filters = {}
        if doc_type:
            filters['type'] = doc_type
        if source:
            filters['source'] = source
        
        documents = vector_service.vector_db.list_documents(
            limit=limit,
            offset=offset,
            filters=filters if filters else None
        )
        
        if not documents:
            click.echo("No documents found.")
            return
        
        click.echo(f"Found {len(documents)} documents:")
        click.echo(f"{'ID':<20} {'Type':<15} {'Source':<15} {'Content Preview':<50}")
        click.echo("-" * 100)
        
        for doc in documents:
            doc_type_str = doc.metadata.get('type', 'Unknown')
            source_str = doc.source or 'N/A'
            preview = doc.content[:47] + "..." if len(doc.content) > 50 else doc.content
            
            click.echo(f"{doc.id:<20} {doc_type_str:<15} {source_str:<15} {preview:<50}")
    
    except Exception as e:
        click.echo(f"List failed: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
