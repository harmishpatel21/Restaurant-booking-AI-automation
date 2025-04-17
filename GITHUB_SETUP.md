# GitHub Setup Guide

This guide will help you set up this project with your GitHub repository.

## Prerequisites

- A GitHub account
- Git installed on your local machine (if you're cloning the repository locally)

## Option 1: Push from Replit to GitHub

### 1. Create a new repository on GitHub

1. Go to [GitHub](https://github.com/) and log in to your account
2. Click on the "+" icon in the top right corner and select "New repository"
3. Name your repository (e.g., "restaurant-booking-system")
4. Choose whether the repository should be public or private
5. Do not initialize the repository with a README, .gitignore, or license
6. Click "Create repository"

### 2. Configure Git in Replit

In your Replit shell, set your Git user information:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Add the GitHub repository as a remote

In your Replit shell, add your GitHub repository as a remote:

```bash
git remote add origin https://github.com/yourusername/your-repository-name.git
```

Replace `yourusername` and `your-repository-name` with your GitHub username and repository name.

### 4. Stage, commit, and push your files

```bash
# Stage all files
git add .

# Commit the files
git commit -m "Initial commit"

# Push to GitHub
git push -u origin main
```

Note: If the branch is called "master" instead of "main", use:

```bash
git push -u origin master
```

### 5. Authentication

When pushing, you will be prompted for your GitHub credentials.

#### Using a Personal Access Token (Recommended)

For security reasons, GitHub now prefers Personal Access Tokens over passwords for authentication:

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token"
3. Give it a name, select at least the "repo" scope, and click "Generate token"
4. Copy your token (store it safely; you won't be able to see it again)
5. Use this token as your password when Git asks for authentication

## Option 2: Clone to Your Local Machine

If you prefer to work on the project locally:

### 1. Export your Replit project

1. In Replit, use the Download as ZIP option to get the code
2. Extract the ZIP file to a folder on your computer

### 2. Initialize a Git repository locally

```bash
cd path/to/extracted/folder
git init
git add .
git commit -m "Initial commit"
```

### 3. Create and connect to your GitHub repository

```bash
git remote add origin https://github.com/yourusername/your-repository-name.git
git push -u origin main
```

## Collaborating on GitHub

Once your project is on GitHub, you can:

1. Add collaborators to your repository
   - Go to your repository → Settings → Manage access → Add people

2. Work with branches for features or bug fixes
   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git add .
   git commit -m "Add new feature"
   git push -u origin feature/new-feature
   ```

3. Create pull requests to merge changes
   - Go to your repository on GitHub
   - Click on "Pull requests" → "New pull request"
   - Select the branch to merge and create the pull request

## Further Git/GitHub Resources

- [GitHub Guides](https://guides.github.com/)
- [GitHub Learning Lab](https://lab.github.com/)
- [Pro Git Book](https://git-scm.com/book/en/v2)
- [GitHub CLI](https://cli.github.com/) - Command line tool for GitHub