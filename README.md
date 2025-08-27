# Proposal Master
> **AI-Powered Automated RFP & Tender Response System with Intelligent Opportunity Discovery**

An enterprise-grade system that automatically discovers open tenders, analyzes RFP requirements, generates competitive proposals, and submits responses to maximize revenue through automated bid management.

## ✨ Key Features

### 🎯 **AI-Powered Lead Generation**
- **Prospect Discovery**: Automated scanning of UN/NGO procurement and funding opportunities
- **Decision Maker Intelligence**: AI identification of key contacts and influencers
- **Opportunity Scoring**: Smart qualification and prioritization of prospects
- **Pipeline Management**: Automated tracking from lead to closed revenue

### � **Revenue Optimization** 
- **Outreach Automation**: AI-powered contact campaigns and relationship building
- **Win Rate Analytics**: Continuous improvement of conversion strategies
- **Revenue Forecasting**: Predictive modeling for business planning
- **Competitive Intelligence**: Real-time monitoring of market opportunities

### 🔧 **Enterprise Architecture**
- **FastAPI REST API**: Production-ready API with comprehensive lead management endpoints
- **Multi-Channel Integration**: LinkedIn, email, CRM, and procurement platform connections
- **Real-Time Monitoring**: Continuous scanning for new opportunities and market changes
- **Anti-Scraping System**: Advanced rate limiting, proxy management, and CAPTCHA solving

## 🏗️ System Architecture

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      TaskMaster Layer                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │   Task Planning │ │   Orchestration │ │   Progress      │   │
│  │   & Breakdown   │ │   & Scheduling  │ │   Tracking      │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                    Automated RFP Discovery Layer               │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │   Tender        │ │   Opportunity   │ │   Deadline      │   │
│  │   Scanning      │ │   Filtering     │ │   Management    │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                   AI Proposal Generation Layer                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ Requirements    │ │ Content         │ │ Compliance      │   │
│  │ Analysis        │ │ Generation      │ │ Verification    │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                     Core Services                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ Portal          │ │ Document        │ │ Submission      │   │
│  │ Integration     │ │ Processing      │ │ Automation      │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                      API Layer                                 │
│         FastAPI REST Endpoints + Interactive Documentation     │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **8GB+ RAM** (recommended for ML models)  
- **API Keys**: OpenAI, Anthropic, or Perplexity for AI features

### Installation & Setup

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd proposal_master
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

### Environment Configuration

The system uses a `.env` file to manage API keys and other secrets. To get started, copy the example file:

```bash
cp .env.example .env
```

Then, edit the `.env` file and add your API keys. At least one of the following AI provider keys is required for the system to function correctly:

-   `ANTHROPIC_API_KEY`: For using Anthropic's Claude models.
-   `OPENAI_API_KEY`: For using OpenAI's GPT models.
-   `PERPLEXITY_API_KEY`: For using Perplexity's models for research.

The other keys listed in the `.env.example` file are optional and can be configured as needed.

2. **Configure API keys**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # OPENAI_API_KEY="sk-proj-..."
   # ANTHROPIC_API_KEY="sk-ant-api03-..."  
   # PERPLEXITY_API_KEY="pplx-..."
   ```

3. **Initialize TaskMaster**:
   ```bash
   taskmaster init
   taskmaster models --setup  # Configure AI models interactively
   ```

### Running the System

**Start the API Server**:
```bash
python start_api.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs  
```

**Run Main Application**:
```bash
python main.py
```

**Automated RFP Commands**:
```bash
taskmaster tender-scan --portals="UNGM,UN-Global"   # Discover open tenders
taskmaster analyze-rfp --tender-id="TID001"         # Extract requirements
taskmaster generate-proposal --tender-id="TID001"   # Create proposal
taskmaster submit-bid --tender-id="TID001"          # Automated submission
```

## ☁️ Cloud Deployment (GCP & Kubernetes)

This section details how to deploy the Proposal Master system to a Google Cloud Platform (GCP) environment using Pulumi for infrastructure management and Kubernetes (k3s) for container orchestration.

### Prerequisites

-   **Google Cloud SDK (`gcloud`)**: Installed and authenticated.
-   **Pulumi CLI**: Installed.
-   **Docker**: Installed locally for building container images.
-   **A Docker/Container Registry**: Such as Google Container Registry (GCR) or Docker Hub, to store your built images.
-   **SSH Key**: An SSH public key located at `~/.ssh/id_rsa.pub`.

### 1. Infrastructure Deployment with Pulumi

The infrastructure is defined in `__main__.py` and managed by Pulumi. It creates a GCP Compute Engine instance and configures it with Docker and k3s.

1.  **Configure Pulumi for GCP**:
    Set your GCP project and region for Pulumi.

    ```bash
    pulumi config set gcp:project YOUR_GCP_PROJECT_ID
    pulumi config set gcp:region YOUR_GCP_REGION
    ```

2.  **Deploy the Infrastructure**:
    Run `pulumi up` to preview and deploy the resources.

    ```bash
    pulumi up
    ```

    After a successful deployment, Pulumi will output the `instance_ip` of your new server.

### 2. Build and Push Container Images

The application is split into two containers: one for the backend and one for the frontend.

1.  **Build the Backend Image**:

    ```bash
    docker build -f Dockerfile.backend -t YOUR_REGISTRY/proposal-master-backend:latest .
    ```

2.  **Build the Frontend Image**:

    ```bash
    docker build -f Dockerfile.frontend -t YOUR_REGISTRY/proposal-master-frontend:latest .
    ```

3.  **Push the Images to Your Registry**:

    ```bash
    docker push YOUR_REGISTRY/proposal-master-backend:latest
    docker push YOUR_REGISTRY/proposal-master-frontend:latest
    ```

    **Note**: Remember to replace `YOUR_REGISTRY` with your container registry's path (e.g., `gcr.io/your-gcp-project-id`).

### 3. Deploy Application to Kubernetes

1.  **Update Image Names in `k8s.yml`**:
    Open the `k8s.yml` file and replace the placeholder image names (`your-registry/proposal-master-backend:latest` and `your-registry/proposal-master-frontend:latest`) with the actual image paths from the previous step.

2.  **Connect to the Server**:
    SSH into the newly created GCP instance.

    ```bash
    ssh ubuntu@<INSTANCE_IP>
    ```

3.  **Apply Kubernetes Manifests**:
    Once on the server, you can apply the Kubernetes configuration. The `k8s.yml` file will need to be copied to the server or made available. For simplicity, you can copy its content and create it on the server.

    ```bash
    # On the GCP instance
    kubectl apply -f /path/to/your/k8s.yml
    ```
    *A simpler alternative is to use the k3s kubeconfig on your local machine to deploy remotely.*

### 4. Access the Application

Once the Kubernetes pods are running, you can access the application in your browser using the server's IP address.

-   **Frontend UI**: `http://<INSTANCE_IP>/`
-   **Backend API**: `http://<INSTANCE_IP>/api/` (e.g., `http://<INSTANCE_IP>/api/v1/health`)

The NGINX Ingress controller will automatically route requests to the correct service.

## 📁 Project Structure

```
proposal_master/
├── src/
│   ├── core/                    # Core system components
│   │   ├── document_processor.py
│   │   ├── rag_system.py
│   │   └── similarity_engine.py
│   ├── modules/                 # Automated RFP processing modules
│   │   ├── discovery/          # Tender scanning and opportunity detection
│   │   ├── analysis/           # RFP requirement extraction and compliance
│   │   ├── intelligence/       # Competitive analysis and win probability
│   │   ├── generation/         # Automated proposal content creation
│   │   └── submission/         # Portal integration and automated bidding
│   ├── agents/                 # AI agent implementations
│   ├── prompts/                # AI prompt templates
│   ├── utils/                  # Utility functions
│   └── api/                    # REST API endpoints
├── data/                       # Data storage
│   ├── documents/              # Document collections
│   ├── embeddings/             # Vector embeddings
│   └── cache/                  # Temporary files
├── logs/                       # Application logs
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Development

### Adding New Modules
1. Create module directory under `src/modules/`
2. Implement core functionality
3. Add corresponding agent in `src/agents/`
4. Update API routes in `src/api/routes/`

### Code Style
This project follows Python best practices:
- **PEP 8** style guidelines
- **Type hints** for all functions
- **Docstrings** for classes and methods
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
flake8 src/
mypy src/
```

## 🤖 AI Integration

The system supports integration with various AI services:
- **OpenAI GPT models** for content generation
- **Anthropic Claude** for analysis and reasoning
- **Sentence Transformers** for embeddings
- **Custom fine-tuned models** for domain-specific tasks

## 📊 Data Management

### Document Storage
- **RFP Samples**: `data/documents/rfp_samples/`
- **Case Studies**: `data/documents/case_studies/`
- **Industry Reports**: `data/documents/industry_reports/`
- **Templates**: `data/documents/templates/`

### Embeddings and Cache
- **Vector Index**: `data/embeddings/rag_index.pkl`
- **Temporary Files**: `data/cache/temp_files/`

## 🔐 Security and Compliance

- Secure document handling and storage
- API authentication and authorization
- Compliance checking for industry standards
- Data privacy and confidentiality measures

## 🚧 Roadmap

- [ ] Complete AI agent implementations
- [ ] Web-based user interface
- [ ] Advanced analytics dashboard
- [ ] Integration with CRM systems
- [ ] Multi-language support
- [ ] Cloud deployment options

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure code quality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is open source. Feel free to modify and distribute as needed.

## 📞 Support

For questions, issues, or feature requests, please open an issue in the repository.

---

**Proposal Master** - Transforming proposal management with AI intelligence 🚀
