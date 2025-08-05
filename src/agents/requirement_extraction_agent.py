"""
Requirement Extraction Agent for intelligent requirement analysis and categorization.

This agent specializes in extracting, categorizing, and analyzing requirements
from RFP documents with AI-powered analysis and structured output.
"""

import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

from .base_agent import BaseAgent
from ..prompts.analysis_prompts import AnalysisPrompts

logger = logging.getLogger(__name__)


class RequirementType(Enum):
    """Enumeration of requirement types."""
    FUNCTIONAL = "functional"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    OPERATIONAL = "operational"


class RequirementPriority(Enum):
    """Enumeration of requirement priorities."""
    MANDATORY = "mandatory"
    IMPORTANT = "important"
    OPTIONAL = "optional"
    PREFERRED = "preferred"


class RequirementComplexity(Enum):
    """Enumeration of requirement complexity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Requirement:
    """Data class representing a single requirement."""
    id: str
    text: str
    type: RequirementType
    priority: RequirementPriority
    complexity: RequirementComplexity
    section: str
    dependencies: List[str]
    verification_method: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    risk_level: Optional[str] = None
    estimated_effort: Optional[str] = None
    compliance_standards: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.compliance_standards is None:
            self.compliance_standards = []


class RequirementExtractionAgent(BaseAgent):
    """
    Specialized agent for extracting and analyzing requirements from documents.
    
    Capabilities:
    - AI-powered requirement extraction from natural language
    - Requirement categorization and prioritization
    - Dependency mapping and analysis
    - Compliance requirement identification
    - Verification method suggestions
    - Risk assessment for individual requirements
    - Traceability matrix generation
    """
    
    def __init__(self, ai_client: Optional[Any] = None):
        super().__init__(ai_client)
        self.requirement_patterns = {
            # Strong requirement indicators
            'shall_patterns': [
                r'(?i)(?:the\s+)?(?:system|solution|contractor|vendor|provider|application)\s+shall\s+([^.]+)',
                r'(?i)shall\s+([^.]+)',
            ],
            'must_patterns': [
                r'(?i)(?:the\s+)?(?:system|solution|contractor|vendor|provider|application)\s+must\s+([^.]+)',
                r'(?i)must\s+([^.]+)',
            ],
            'required_patterns': [
                r'(?i)(?:is\s+)?required\s+to\s+([^.]+)',
                r'(?i)(?:are\s+)?required\s+([^.]+)',
            ],
            'mandatory_patterns': [
                r'(?i)(?:is\s+)?mandatory\s+([^.]+)',
                r'(?i)mandatory\s+([^.]+)',
            ],
            # Weaker requirement indicators
            'should_patterns': [
                r'(?i)(?:the\s+)?(?:system|solution|contractor|vendor|provider|application)\s+should\s+([^.]+)',
                r'(?i)should\s+([^.]+)',
            ],
            'will_patterns': [
                r'(?i)(?:the\s+)?(?:system|solution|contractor|vendor|provider|application)\s+will\s+([^.]+)',
                r'(?i)will\s+([^.]+)',
            ]
        }
        
        self.compliance_patterns = {
            'security_standards': [
                r'(?i)(NIST\s+\d+)', r'(?i)(ISO\s+\d+)', r'(?i)(SOC\s+\d+)',
                r'(?i)(FISMA)', r'(?i)(FedRAMP)', r'(?i)(FIPS\s+\d+)'
            ],
            'industry_standards': [
                r'(?i)(HIPAA)', r'(?i)(PCI\s+DSS)', r'(?i)(GDPR)',
                r'(?i)(SOX)', r'(?i)(CMMI)', r'(?i)(ITIL)'
            ],
            'government_standards': [
                r'(?i)(FAR)', r'(?i)(DFAR)', r'(?i)(Section\s+508)',
                r'(?i)(GSA)', r'(?i)(OMB)', r'(?i)(NARA)'
            ]
        }
    
    async def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process requirement extraction request.
        
        Args:
            inputs: Dictionary containing:
                - document_content: Text content to analyze
                - extraction_mode: 'ai_powered', 'pattern_based', or 'hybrid'
                - include_dependencies: Boolean for dependency analysis
                - generate_traceability: Boolean for traceability matrix
                - compliance_focus: List of compliance standards to focus on
        
        Returns:
            Dictionary containing extracted requirements and analysis
        """
        try:
            document_content = inputs.get('document_content', '')
            extraction_mode = inputs.get('extraction_mode', 'hybrid')
            include_dependencies = inputs.get('include_dependencies', True)
            generate_traceability = inputs.get('generate_traceability', True)
            compliance_focus = inputs.get('compliance_focus', [])
            
            logger.info(f"Starting requirement extraction with {extraction_mode} mode")
            
            extraction_result = {
                'extraction_metadata': {
                    'mode': extraction_mode,
                    'timestamp': str(asyncio.get_event_loop().time()),
                    'agent_version': '1.0.0',
                    'document_length': len(document_content.split())
                },
                'requirements': [],
                'analysis_summary': {},
                'compliance_requirements': [],
                'critical_success_factors': []
            }
            
            # Extract requirements based on mode
            if extraction_mode == 'ai_powered' and self.ai_client:
                extraction_result.update(await self._ai_requirement_extraction(document_content))
            elif extraction_mode == 'pattern_based':
                extraction_result.update(await self._pattern_based_extraction(document_content))
            else:  # hybrid mode
                extraction_result.update(await self._hybrid_extraction(document_content))
            
            # Post-processing analysis
            if extraction_result['requirements']:
                # Dependency analysis
                if include_dependencies:
                    extraction_result['dependency_analysis'] = await self._analyze_dependencies(
                        extraction_result['requirements']
                    )
                
                # Compliance analysis
                if compliance_focus:
                    extraction_result['compliance_analysis'] = await self._analyze_compliance_requirements(
                        extraction_result['requirements'], compliance_focus
                    )
                
                # Generate analysis summary
                extraction_result['analysis_summary'] = await self._generate_analysis_summary(
                    extraction_result['requirements']
                )
                
                # Generate traceability matrix
                if generate_traceability:
                    extraction_result['traceability_matrix'] = await self._generate_traceability_matrix(
                        extraction_result['requirements']
                    )
                
                # Identify critical success factors
                extraction_result['critical_success_factors'] = await self._identify_critical_success_factors(
                    extraction_result['requirements']
                )
            
            logger.info(f"Requirement extraction completed: {len(extraction_result['requirements'])} requirements found")
            return extraction_result
            
        except Exception as e:
            logger.error(f"Requirement extraction failed: {str(e)}")
            return await self._fallback_extraction(inputs)
    
    async def _ai_requirement_extraction(self, content: str) -> Dict[str, Any]:
        """Extract requirements using AI-powered analysis."""
        try:
            # Get structured prompt for requirement extraction
            prompt = AnalysisPrompts.get_prompt('requirement_extraction', document_content=content)
            system_prompt = AnalysisPrompts.get_system_prompt()
            
            response = await self.ai_client.generate(
                system_prompt=system_prompt,
                user_prompt=prompt
            )
            
            # Parse AI response
            try:
                ai_result = json.loads(response)
                requirements = []
                
                for req_data in ai_result.get('requirements', []):
                    requirement = Requirement(
                        id=req_data.get('id', f"REQ-{len(requirements)+1:03d}"),
                        text=req_data.get('text', ''),
                        type=RequirementType(req_data.get('type', 'functional')),
                        priority=RequirementPriority(req_data.get('priority', 'important')),
                        complexity=RequirementComplexity(req_data.get('complexity', 'medium')),
                        section=req_data.get('section', 'unknown'),
                        dependencies=req_data.get('dependencies', [])
                    )
                    requirements.append(requirement)
                
                return {
                    'requirements': [asdict(req) for req in requirements],
                    'ai_analysis_summary': ai_result.get('summary', {}),
                    'extraction_method': 'ai_powered'
                }
                
            except json.JSONDecodeError:
                logger.warning("AI response was not valid JSON, falling back to pattern extraction")
                return await self._pattern_based_extraction(content)
            
        except Exception as e:
            logger.error(f"AI requirement extraction failed: {str(e)}")
            return await self._pattern_based_extraction(content)
    
    async def _pattern_based_extraction(self, content: str) -> Dict[str, Any]:
        """Extract requirements using pattern matching."""
        requirements = []
        req_counter = 1
        
        # Extract requirements using patterns
        for pattern_type, patterns in self.requirement_patterns.items():
            priority = self._map_pattern_to_priority(pattern_type)
            
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                
                for match in matches:
                    requirement_text = match.group(1) if match.groups() else match.group()
                    requirement_text = requirement_text.strip()
                    
                    if len(requirement_text) > 10:  # Filter out very short matches
                        requirement = Requirement(
                            id=f"REQ-{req_counter:03d}",
                            text=requirement_text,
                            type=self._classify_requirement_type(requirement_text),
                            priority=priority,
                            complexity=self._assess_requirement_complexity(requirement_text),
                            section=self._identify_section_context(content, match.start()),
                            dependencies=[]
                        )
                        
                        # Add compliance standards if found
                        requirement.compliance_standards = self._extract_compliance_standards(requirement_text)
                        
                        requirements.append(requirement)
                        req_counter += 1
        
        # Remove duplicates based on text similarity
        unique_requirements = self._deduplicate_requirements(requirements)
        
        return {
            'requirements': [asdict(req) for req in unique_requirements],
            'extraction_method': 'pattern_based',
            'patterns_matched': len(requirements),
            'unique_requirements': len(unique_requirements)
        }
    
    async def _hybrid_extraction(self, content: str) -> Dict[str, Any]:
        """Extract requirements using hybrid AI + pattern approach."""
        # Start with pattern-based extraction for baseline
        pattern_result = await self._pattern_based_extraction(content)
        
        # Enhance with AI analysis if available
        if self.ai_client:
            try:
                ai_result = await self._ai_requirement_extraction(content)
                
                # Merge results intelligently
                merged_requirements = self._merge_extraction_results(
                    pattern_result['requirements'],
                    ai_result.get('requirements', [])
                )
                
                return {
                    'requirements': merged_requirements,
                    'extraction_method': 'hybrid',
                    'pattern_count': len(pattern_result['requirements']),
                    'ai_count': len(ai_result.get('requirements', [])),
                    'merged_count': len(merged_requirements)
                }
                
            except Exception as e:
                logger.warning(f"AI enhancement failed, using pattern results: {str(e)}")
                return pattern_result
        else:
            return pattern_result
    
    async def _analyze_dependencies(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze dependencies between requirements."""
        dependency_analysis = {
            'dependency_map': {},
            'circular_dependencies': [],
            'critical_path': [],
            'dependency_levels': {}
        }
        
        # Build dependency map
        for req in requirements:
            req_id = req['id']
            dependencies = req.get('dependencies', [])
            
            dependency_analysis['dependency_map'][req_id] = {
                'depends_on': dependencies,
                'dependents': []
            }
        
        # Find dependents (reverse mapping)
        for req in requirements:
            req_id = req['id']
            for dep_id in req.get('dependencies', []):
                if dep_id in dependency_analysis['dependency_map']:
                    dependency_analysis['dependency_map'][dep_id]['dependents'].append(req_id)
        
        # Identify circular dependencies
        dependency_analysis['circular_dependencies'] = self._find_circular_dependencies(
            dependency_analysis['dependency_map']
        )
        
        # Calculate dependency levels
        dependency_analysis['dependency_levels'] = self._calculate_dependency_levels(
            dependency_analysis['dependency_map']
        )
        
        return dependency_analysis
    
    async def _analyze_compliance_requirements(self, requirements: List[Dict[str, Any]], 
                                             focus_standards: List[str]) -> Dict[str, Any]:
        """Analyze compliance requirements and standards."""
        compliance_analysis = {
            'standards_coverage': {},
            'compliance_gaps': [],
            'high_risk_requirements': [],
            'certification_requirements': []
        }
        
        # Analyze coverage for each standard
        for standard in focus_standards:
            compliance_analysis['standards_coverage'][standard] = {
                'requirements': [],
                'coverage_score': 0.0,
                'critical_gaps': []
            }
        
        # Check each requirement for compliance indicators
        for req in requirements:
            req_text = req['text'].lower()
            req_standards = req.get('compliance_standards', [])
            
            # Map to focus standards
            for standard in focus_standards:
                if standard.lower() in req_text or any(std.lower() == standard.lower() for std in req_standards):
                    compliance_analysis['standards_coverage'][standard]['requirements'].append(req['id'])
            
            # Identify high-risk compliance requirements
            if req['priority'] == 'mandatory' and req['type'] in ['compliance', 'security']:
                compliance_analysis['high_risk_requirements'].append({
                    'requirement_id': req['id'],
                    'text': req['text'],
                    'risk_factors': self._assess_compliance_risk_factors(req)
                })
        
        # Calculate coverage scores
        for standard in focus_standards:
            req_count = len(compliance_analysis['standards_coverage'][standard]['requirements'])
            total_reqs = len([r for r in requirements if r['type'] == 'compliance'])
            compliance_analysis['standards_coverage'][standard]['coverage_score'] = (
                req_count / max(total_reqs, 1)
            )
        
        return compliance_analysis
    
    async def _generate_analysis_summary(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive analysis summary."""
        total_requirements = len(requirements)
        
        # Count by type
        type_breakdown = {}
        for req in requirements:
            req_type = req['type']
            type_breakdown[req_type] = type_breakdown.get(req_type, 0) + 1
        
        # Count by priority
        priority_breakdown = {}
        for req in requirements:
            priority = req['priority']
            priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
        
        # Count by complexity
        complexity_breakdown = {}
        for req in requirements:
            complexity = req['complexity']
            complexity_breakdown[complexity] = complexity_breakdown.get(complexity, 0) + 1
        
        # Calculate risk metrics
        high_complexity_count = complexity_breakdown.get('high', 0) + complexity_breakdown.get('critical', 0)
        mandatory_count = priority_breakdown.get('mandatory', 0)
        
        return {
            'total_requirements': total_requirements,
            'type_breakdown': type_breakdown,
            'priority_breakdown': priority_breakdown,
            'complexity_breakdown': complexity_breakdown,
            'risk_metrics': {
                'high_complexity_percentage': (high_complexity_count / max(total_requirements, 1)) * 100,
                'mandatory_percentage': (mandatory_count / max(total_requirements, 1)) * 100,
                'overall_risk_score': self._calculate_overall_risk_score(requirements)
            },
            'recommendations': self._generate_recommendations(requirements)
        }
    
    async def _generate_traceability_matrix(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate requirements traceability matrix."""
        matrix = {
            'requirements_by_section': {},
            'type_mapping': {},
            'priority_mapping': {},
            'verification_methods': {}
        }
        
        # Group by section
        for req in requirements:
            section = req.get('section', 'unknown')
            if section not in matrix['requirements_by_section']:
                matrix['requirements_by_section'][section] = []
            matrix['requirements_by_section'][section].append(req['id'])
        
        # Group by type
        for req in requirements:
            req_type = req['type']
            if req_type not in matrix['type_mapping']:
                matrix['type_mapping'][req_type] = []
            matrix['type_mapping'][req_type].append(req['id'])
        
        # Group by priority
        for req in requirements:
            priority = req['priority']
            if priority not in matrix['priority_mapping']:
                matrix['priority_mapping'][priority] = []
            matrix['priority_mapping'][priority].append(req['id'])
        
        # Suggest verification methods
        for req in requirements:
            verification_method = self._suggest_verification_method(req)
            matrix['verification_methods'][req['id']] = verification_method
        
        return matrix
    
    async def _identify_critical_success_factors(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify critical success factors from requirements."""
        critical_factors = []
        
        # High-priority, high-complexity requirements
        for req in requirements:
            if req['priority'] == 'mandatory' and req['complexity'] in ['high', 'critical']:
                critical_factors.append({
                    'type': 'high_risk_requirement',
                    'requirement_id': req['id'],
                    'description': req['text'],
                    'risk_level': 'high',
                    'mitigation_needed': True
                })
        
        # Requirements with many dependencies
        dependency_counts = {}
        for req in requirements:
            dep_count = len(req.get('dependencies', []))
            if dep_count > 0:
                dependency_counts[req['id']] = dep_count
        
        # Top 20% of requirements by dependency count
        if dependency_counts:
            threshold = sorted(dependency_counts.values(), reverse=True)[
                max(0, len(dependency_counts) // 5)
            ]
            
            for req_id, count in dependency_counts.items():
                if count >= threshold:
                    req = next(r for r in requirements if r['id'] == req_id)
                    critical_factors.append({
                        'type': 'high_dependency_requirement',
                        'requirement_id': req_id,
                        'description': req['text'],
                        'dependency_count': count,
                        'coordination_critical': True
                    })
        
        # Compliance requirements
        for req in requirements:
            if req['type'] == 'compliance' and req['priority'] == 'mandatory':
                critical_factors.append({
                    'type': 'compliance_requirement',
                    'requirement_id': req['id'],
                    'description': req['text'],
                    'compliance_standards': req.get('compliance_standards', []),
                    'audit_critical': True
                })
        
        return critical_factors
    
    # Helper methods
    def _map_pattern_to_priority(self, pattern_type: str) -> RequirementPriority:
        """Map pattern type to requirement priority."""
        priority_map = {
            'shall_patterns': RequirementPriority.MANDATORY,
            'must_patterns': RequirementPriority.MANDATORY,
            'required_patterns': RequirementPriority.MANDATORY,
            'mandatory_patterns': RequirementPriority.MANDATORY,
            'should_patterns': RequirementPriority.IMPORTANT,
            'will_patterns': RequirementPriority.IMPORTANT
        }
        return priority_map.get(pattern_type, RequirementPriority.IMPORTANT)
    
    def _classify_requirement_type(self, requirement_text: str) -> RequirementType:
        """Classify requirement type based on text content."""
        text_lower = requirement_text.lower()
        
        # Technical indicators
        technical_keywords = ['system', 'software', 'hardware', 'interface', 'api', 'database']
        if any(keyword in text_lower for keyword in technical_keywords):
            return RequirementType.TECHNICAL
        
        # Security indicators
        security_keywords = ['security', 'authentication', 'authorization', 'encryption', 'access']
        if any(keyword in text_lower for keyword in security_keywords):
            return RequirementType.SECURITY
        
        # Performance indicators
        performance_keywords = ['performance', 'speed', 'latency', 'throughput', 'response time']
        if any(keyword in text_lower for keyword in performance_keywords):
            return RequirementType.PERFORMANCE
        
        # Compliance indicators
        compliance_keywords = ['comply', 'standard', 'regulation', 'certification', 'audit']
        if any(keyword in text_lower for keyword in compliance_keywords):
            return RequirementType.COMPLIANCE
        
        # Default to functional
        return RequirementType.FUNCTIONAL
    
    def _assess_requirement_complexity(self, requirement_text: str) -> RequirementComplexity:
        """Assess requirement complexity based on text analysis."""
        text_lower = requirement_text.lower()
        
        # High complexity indicators
        high_complexity_keywords = [
            'integrate', 'migration', 'complex', 'multiple', 'various',
            'enterprise', 'scalable', 'real-time', 'distributed'
        ]
        
        # Critical complexity indicators
        critical_keywords = [
            'mission critical', 'high availability', 'zero downtime',
            'disaster recovery', 'business continuity'
        ]
        
        if any(keyword in text_lower for keyword in critical_keywords):
            return RequirementComplexity.CRITICAL
        elif any(keyword in text_lower for keyword in high_complexity_keywords):
            return RequirementComplexity.HIGH
        elif len(requirement_text.split()) > 20:
            return RequirementComplexity.MEDIUM
        else:
            return RequirementComplexity.LOW
    
    def _identify_section_context(self, content: str, position: int) -> str:
        """Identify document section where requirement was found."""
        # Get text before the requirement to find section header
        before_text = content[:position]
        lines = before_text.split('\n')
        
        # Look for section headers in reverse
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if re.match(r'^\d+\.?\s+[A-Z]', line) or line.isupper():
                return line[:50]  # Return first 50 chars of section header
        
        return 'unknown'
    
    def _extract_compliance_standards(self, requirement_text: str) -> List[str]:
        """Extract compliance standards mentioned in requirement text."""
        standards = []
        
        for category, patterns in self.compliance_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, requirement_text)
                standards.extend(matches)
        
        return list(set(standards))  # Remove duplicates
    
    def _deduplicate_requirements(self, requirements: List[Requirement]) -> List[Requirement]:
        """Remove duplicate requirements based on text similarity."""
        unique_requirements = []
        seen_texts = set()
        
        for req in requirements:
            # Simple deduplication based on normalized text
            normalized_text = re.sub(r'\s+', ' ', req.text.lower().strip())
            
            if normalized_text not in seen_texts:
                seen_texts.add(normalized_text)
                unique_requirements.append(req)
        
        return unique_requirements
    
    def _merge_extraction_results(self, pattern_results: List[Dict], ai_results: List[Dict]) -> List[Dict]:
        """Merge pattern-based and AI-based extraction results."""
        # Simple merge - prefer AI results for quality, supplement with pattern results
        merged = list(ai_results)  # Start with AI results
        
        # Add pattern results that don't overlap significantly
        for pattern_req in pattern_results:
            is_duplicate = False
            pattern_text = pattern_req['text'].lower()
            
            for ai_req in ai_results:
                ai_text = ai_req['text'].lower()
                # Simple similarity check
                if self._text_similarity(pattern_text, ai_text) > 0.7:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                merged.append(pattern_req)
        
        return merged
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity between two strings."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / max(len(union), 1)
    
    def _find_circular_dependencies(self, dependency_map: Dict) -> List[List[str]]:
        """Find circular dependencies in requirement graph."""
        # Simplified circular dependency detection
        circular_deps = []
        visited = set()
        
        def dfs(node, path):
            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                circular_deps.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            path.append(node)
            
            for dep in dependency_map.get(node, {}).get('depends_on', []):
                if dep in dependency_map:
                    dfs(dep, path.copy())
        
        for req_id in dependency_map:
            if req_id not in visited:
                dfs(req_id, [])
        
        return circular_deps
    
    def _calculate_dependency_levels(self, dependency_map: Dict) -> Dict[str, int]:
        """Calculate dependency levels for requirements."""
        levels = {}
        
        def calculate_level(req_id, visited=None):
            if visited is None:
                visited = set()
            
            if req_id in visited:
                return 0  # Circular dependency
            
            if req_id in levels:
                return levels[req_id]
            
            visited.add(req_id)
            dependencies = dependency_map.get(req_id, {}).get('depends_on', [])
            
            if not dependencies:
                levels[req_id] = 0
            else:
                max_dep_level = max(
                    calculate_level(dep, visited.copy()) for dep in dependencies
                    if dep in dependency_map
                )
                levels[req_id] = max_dep_level + 1
            
            return levels[req_id]
        
        for req_id in dependency_map:
            calculate_level(req_id)
        
        return levels
    
    def _assess_compliance_risk_factors(self, requirement: Dict[str, Any]) -> List[str]:
        """Assess risk factors for compliance requirements."""
        risk_factors = []
        
        if requirement['complexity'] in ['high', 'critical']:
            risk_factors.append('high_implementation_complexity')
        
        if requirement.get('compliance_standards'):
            risk_factors.append('regulatory_oversight_required')
        
        if 'audit' in requirement['text'].lower():
            risk_factors.append('audit_trail_required')
        
        if 'security' in requirement['text'].lower():
            risk_factors.append('security_implications')
        
        return risk_factors
    
    def _calculate_overall_risk_score(self, requirements: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score for requirement set."""
        if not requirements:
            return 0.0
        
        risk_score = 0.0
        
        for req in requirements:
            # Weight by priority
            priority_weight = {
                'mandatory': 3.0,
                'important': 2.0,
                'optional': 1.0,
                'preferred': 1.5
            }.get(req['priority'], 1.0)
            
            # Weight by complexity
            complexity_weight = {
                'critical': 4.0,
                'high': 3.0,
                'medium': 2.0,
                'low': 1.0
            }.get(req['complexity'], 1.0)
            
            # Calculate requirement risk
            req_risk = (priority_weight * complexity_weight) / 12.0  # Normalize to 0-1
            risk_score += req_risk
        
        return min(risk_score / len(requirements), 1.0)  # Average and cap at 1.0
    
    def _generate_recommendations(self, requirements: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on requirement analysis."""
        recommendations = []
        
        # High complexity recommendations
        high_complexity_count = len([r for r in requirements if r['complexity'] in ['high', 'critical']])
        if high_complexity_count > len(requirements) * 0.3:
            recommendations.append("Consider phased implementation approach due to high number of complex requirements")
        
        # Dependency recommendations
        high_dependency_reqs = [r for r in requirements if len(r.get('dependencies', [])) > 3]
        if high_dependency_reqs:
            recommendations.append("Prioritize dependency management and coordination for interconnected requirements")
        
        # Compliance recommendations
        compliance_reqs = [r for r in requirements if r['type'] == 'compliance']
        if compliance_reqs:
            recommendations.append("Establish compliance validation checkpoints throughout development")
        
        # Resource recommendations
        mandatory_count = len([r for r in requirements if r['priority'] == 'mandatory'])
        if mandatory_count > len(requirements) * 0.7:
            recommendations.append("Allocate additional resources for high number of mandatory requirements")
        
        return recommendations
    
    def _suggest_verification_method(self, requirement: Dict[str, Any]) -> str:
        """Suggest verification method for requirement."""
        req_type = requirement['type']
        complexity = requirement['complexity']
        
        if req_type == 'functional':
            return 'functional_testing' if complexity in ['low', 'medium'] else 'integration_testing'
        elif req_type == 'technical':
            return 'technical_review_and_testing'
        elif req_type == 'performance':
            return 'performance_testing'
        elif req_type == 'security':
            return 'security_audit_and_penetration_testing'
        elif req_type == 'compliance':
            return 'compliance_audit_and_documentation_review'
        else:
            return 'review_and_acceptance_testing'
    
    async def _fallback_extraction(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback extraction when main processing fails."""
        logger.info("Using fallback requirement extraction")
        
        try:
            content = inputs.get('document_content', '')
            
            # Very basic pattern matching as fallback
            basic_requirements = []
            
            # Look for simple "shall" statements
            shall_matches = re.findall(r'(?i)shall\s+([^.]+)', content)
            for i, match in enumerate(shall_matches[:10]):  # Limit to 10
                basic_requirements.append({
                    'id': f'REQ-{i+1:03d}',
                    'text': match.strip(),
                    'type': 'functional',
                    'priority': 'mandatory',
                    'complexity': 'medium',
                    'section': 'unknown',
                    'dependencies': []
                })
            
            return {
                'requirements': basic_requirements,
                'extraction_method': 'fallback',
                'analysis_summary': {
                    'total_requirements': len(basic_requirements),
                    'extraction_quality': 'basic'
                },
                'error': 'Full extraction failed, basic patterns used'
            }
            
        except Exception as e:
            return {
                'requirements': [],
                'extraction_method': 'failed',
                'error': f'Fallback extraction failed: {str(e)}'
            }
