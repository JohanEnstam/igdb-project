#!/bin/bash
# Deployment script for IGDB Game Recommendation System
# Supports both manual and automated deployment

set -e  # Exit on any error

# Configuration
PROJECT_ID="igdb-recommendation-system"
REGION="europe-west1"
REGISTRY="europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo"
ENVIRONMENT="${1:-staging}"  # Default to staging

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi

    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi

    # Check if we're authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Not authenticated with gcloud. Please run 'gcloud auth login'"
        exit 1
    fi

    # Check if project is set
    if ! gcloud config get-value project | grep -q "$PROJECT_ID"; then
        log_warning "Setting project to $PROJECT_ID"
        gcloud config set project "$PROJECT_ID"
    fi

    log_success "Prerequisites check passed"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."

    local services=("ingestion" "processing" "training")

    for service in "${services[@]}"; do
        log_info "Building igdb-$service image..."

        docker build \
            -f "data_pipeline/$service/Dockerfile" \
            -t "$REGISTRY/igdb-$service:latest" \
            -t "$REGISTRY/igdb-$service:$ENVIRONMENT" \
            .

        log_success "Built igdb-$service image"
    done
}

# Push images to registry
push_images() {
    log_info "Pushing images to registry..."

    # Configure Docker for Artifact Registry
    gcloud auth configure-docker europe-west1-docker.pkg.dev --quiet

    local services=("ingestion" "processing" "training")

    for service in "${services[@]}"; do
        log_info "Pushing igdb-$service image..."

        docker push "$REGISTRY/igdb-$service:latest"
        docker push "$REGISTRY/igdb-$service:$ENVIRONMENT"

        log_success "Pushed igdb-$service image"
    done
}

# Deploy services to Cloud Run
deploy_services() {
    log_info "Deploying services to Cloud Run ($ENVIRONMENT)..."

    # Deploy Data Ingestion Service
    log_info "Deploying Data Ingestion Service..."
    gcloud run deploy "igdb-ingestion$([ "$ENVIRONMENT" != "production" ] && echo "-$ENVIRONMENT")" \
        --image "$REGISTRY/igdb-ingestion:$ENVIRONMENT" \
        --platform managed \
        --region "$REGION" \
        --set-secrets "IGDB_CLIENT_ID=IGDB_CLIENT_ID:latest,IGDB_CLIENT_SECRET=IGDB_CLIENT_SECRET:latest" \
        --set-env-vars "ENVIRONMENT=$ENVIRONMENT" \
        --allow-unauthenticated \
        --memory 1Gi \
        --cpu 1 \
        --max-instances 10 \
        --quiet

    # Deploy Data Processing Service
    log_info "Deploying Data Processing Service..."
    gcloud run deploy "igdb-processing$([ "$ENVIRONMENT" != "production" ] && echo "-$ENVIRONMENT")" \
        --image "$REGISTRY/igdb-processing:$ENVIRONMENT" \
        --platform managed \
        --region "$REGION" \
        --set-env-vars "ENVIRONMENT=$ENVIRONMENT" \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 2 \
        --max-instances 5 \
        --quiet

    # Deploy ML Training Service
    log_info "Deploying ML Training Service..."
    gcloud run deploy "igdb-training$([ "$ENVIRONMENT" != "production" ] && echo "-$ENVIRONMENT")" \
        --image "$REGISTRY/igdb-training:$ENVIRONMENT" \
        --platform managed \
        --region "$REGION" \
        --set-env-vars "ENVIRONMENT=$ENVIRONMENT" \
        --allow-unauthenticated \
        --memory 4Gi \
        --cpu 4 \
        --max-instances 3 \
        --quiet

    log_success "All services deployed successfully"
}

# Test deployment
test_deployment() {
    log_info "Testing deployment..."

    local services=("ingestion" "processing" "training")

    for service in "${services[@]}"; do
        local service_name="igdb-$service$([ "$ENVIRONMENT" != "production" ] && echo "-$ENVIRONMENT")"
        local url=$(gcloud run services describe "$service_name" --region="$REGION" --format="value(status.url)")

        log_info "Testing $service_name at $url"

        # Test health endpoint
        if curl -f "$url/health" > /dev/null 2>&1; then
            log_success "$service_name health check passed"
        else
            log_warning "$service_name health check failed (endpoint may not be implemented yet)"
        fi
    done
}

# Show deployment info
show_deployment_info() {
    log_info "Deployment Information:"
    echo ""
    echo "Environment: $ENVIRONMENT"
    echo "Project: $PROJECT_ID"
    echo "Region: $REGION"
    echo ""
    echo "Deployed Services:"

    local services=("ingestion" "processing" "training")

    for service in "${services[@]}"; do
        local service_name="igdb-$service$([ "$ENVIRONMENT" != "production" ] && echo "-$ENVIRONMENT")"
        local url=$(gcloud run services describe "$service_name" --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "Not deployed")
        echo "  - $service_name: $url"
    done
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    # Add cleanup logic here if needed
}

# Main deployment function
main() {
    log_info "Starting deployment to $ENVIRONMENT environment..."

    # Set up trap for cleanup
    trap cleanup EXIT

    # Run deployment steps
    check_prerequisites
    build_images
    push_images
    deploy_services
    test_deployment
    show_deployment_info

    log_success "Deployment completed successfully! 🚀"
}

# Help function
show_help() {
    echo "IGDB Game Recommendation System - Deployment Script"
    echo ""
    echo "Usage: $0 [ENVIRONMENT]"
    echo ""
    echo "Environments:"
    echo "  staging     - Deploy to staging environment (default)"
    echo "  production  - Deploy to production environment"
    echo ""
    echo "Examples:"
    echo "  $0 staging     # Deploy to staging"
    echo "  $0 production  # Deploy to production"
    echo ""
    echo "Prerequisites:"
    echo "  - gcloud CLI installed and authenticated"
    echo "  - Docker installed"
    echo "  - Access to GCP project: $PROJECT_ID"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    staging|production)
        main
        ;;
    "")
        main
        ;;
    *)
        log_error "Invalid environment: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
