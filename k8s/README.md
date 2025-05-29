# Kubernetes Configuration

This directory contains Kubernetes manifests for deploying the Resume Analyzer application.

## Prerequisites

- Kubernetes cluster
- kubectl configured
- Docker images built and pushed to a container registry

## Deployment Steps

1. Build and push your Docker images:
   ```bash
   # Build frontend image
   docker build -t your-registry/frontend:latest ./frontend
   docker push your-registry/frontend:latest

   # Build backend image
   docker build -t your-registry/backend:latest ./backend
   docker push your-registry/backend:latest
   ```

2. Update the image names in the deployment files:
   - Replace `${FRONTEND_IMAGE}` in `frontend-deployment.yaml`
   - Replace `${BACKEND_IMAGE}` in `backend-deployment.yaml`

3. Apply the configurations:
   ```bash
   kubectl apply -f backend-deployment.yaml
   kubectl apply -f backend-service.yaml
   kubectl apply -f frontend-deployment.yaml
   kubectl apply -f frontend-service.yaml
   ```

4. Verify the deployment:
   ```bash
   kubectl get pods
   kubectl get services
   ```

## Configuration Details

- Frontend runs on port 3000 and is exposed via LoadBalancer on port 80
- Backend runs on port 5000 and is exposed internally via ClusterIP
- Both services are configured with 2 replicas for high availability
- Resource limits and requests are set for both services

## Accessing the Application

Once deployed, you can access the frontend through the LoadBalancer's external IP:
```bash
kubectl get service frontend-service
```

The backend service is only accessible within the cluster and is used by the frontend service. 