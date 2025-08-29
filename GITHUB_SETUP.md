# GitHub Repository Setup Guide

## 🚀 **Setting Up Your GitHub Repository**

### **1. Create a New Repository on GitHub**

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the repository details:
   - **Repository name**: `cancellations-sop`
   - **Description**: `Automated SOP processing for RPT 600 and RPT 908 reports`
   - **Visibility**: Choose Public or Private
   - **Initialize with**: Leave unchecked (we already have files)
5. Click **"Create repository"**

### **2. Connect Your Local Repository to GitHub**

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add the remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/cancellations-sop.git

# Push your code to GitHub
git branch -M main
git push -u origin main
```

### **3. Enable GitHub Actions**

1. Go to your repository on GitHub
2. Click on the **"Actions"** tab
3. Click **"Enable Actions"** if prompted
4. The CI/CD workflows will automatically run on your next push

### **4. Set Up GitHub Secrets (Optional)**

For Docker image publishing to GHCR:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add the following secrets:
   - `DOCKER_USERNAME`: Your GitHub username
   - `DOCKER_PASSWORD`: Your GitHub Personal Access Token

## 🔧 **Repository Features**

### **Automated CI/CD Pipeline**
- **Testing**: Runs on every push and pull request
- **Code Quality**: Linting, formatting, and type checking
- **Docker Building**: Automated Docker image creation
- **Release Automation**: Publishes Docker images on version tags

### **GitHub Actions Workflows**
- **`.github/workflows/ci.yml`**: Continuous Integration
- **`.github/workflows/release.yml`**: Release automation

## 📱 **Deploying Your Streamlit App**

### **Option 1: Streamlit Cloud (Recommended)**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your `cancellations-sop` repository
5. Set the path to: `src/app/main.py`
6. Click **"Deploy"**

### **Option 2: Heroku**

1. Install Heroku CLI
2. Create a `Procfile`:
   ```
   web: streamlit run src/app/main.py --server.port=$PORT --server.address=0.0.0.0
   ```
3. Deploy using Heroku commands

### **Option 3: Docker Deployment**

```bash
# Build and run locally
make docker/build
make docker/run

# Deploy to cloud platforms
docker push your-registry/cancellations-sop
```

## 🌐 **Accessing Your App**

### **Local Development**
```bash
./run.sh
# Open http://localhost:8501
```

### **Production Deployment**
- **Streamlit Cloud**: Your app will be available at a public URL
- **Docker**: Access via your deployment platform
- **GitHub Pages**: Not recommended for Streamlit apps

## 📊 **Repository Structure**

```
cancellations-sop/
├── .github/workflows/     # CI/CD pipelines
├── src/app/               # Main application
├── tests/                 # Test suite
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Development setup
├── Makefile               # Build commands
├── setup.sh               # Environment setup
├── run.sh                 # Application startup
└── README.md              # Documentation
```

## 🔒 **Security Considerations**

1. **Environment Variables**: Never commit `.env` files
2. **API Keys**: Use GitHub Secrets for sensitive data
3. **Access Control**: Set appropriate repository permissions
4. **Dependencies**: Keep dependencies updated

## 📈 **Monitoring & Maintenance**

### **GitHub Actions**
- Monitor CI/CD pipeline success/failure
- Review automated test results
- Check code quality metrics

### **Application Monitoring**
- Streamlit Cloud provides usage analytics
- Docker containers include health checks
- Application logs for debugging

## 🚀 **Next Steps**

1. **Create the GitHub repository** using the steps above
2. **Push your code** to GitHub
3. **Deploy to Streamlit Cloud** for public access
4. **Monitor the CI/CD pipeline** for quality assurance
5. **Share your app** with stakeholders

## 📞 **Support**

- **GitHub Issues**: Use the Issues tab for bugs/features
- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **Documentation**: Check the README.md and PROJECT_SUMMARY.md

---

**🎯 Your Cancellations SOP Processor is ready for GitHub deployment!**
