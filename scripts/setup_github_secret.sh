#!/bin/bash

# Script to set up GitHub Actions secret for automatic deployment
# This script uses GitHub CLI (gh) to add the Fly.io token as a repository secret

echo "=================================="
echo "GitHub Actions Secret Setup Script"
echo "=================================="

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo ""
    echo "To install GitHub CLI:"
    echo "  macOS: brew install gh"
    echo "  Linux: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo ""
    echo "After installing, run: gh auth login"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI."
    echo "Please run: gh auth login"
    exit 1
fi

# Repository details
REPO="ChipsMetaverse/gvses-market-insights"
SECRET_NAME="FLY_API_TOKEN"

# The Fly.io deploy token
FLY_TOKEN='FlyV1 fm2_lJPECAAAAAAACT/jxBBq26uWKAMqNp9LRxTyCJcIwrVodHRwczovL2FwaS5mbHkuaW8vdjGWAJLOABGjiB8Lk7lodHRwczovL2FwaS5mbHkuaW8vYWFhL3YxxDxowu25il11te9cJ5o1zp7s3ue9PTjW6XyClra0xsXJQbJtsw5ioVLqVSnfPoGRwBdwyYgDODP/9AjP0tDETous+NbaU5rpbiONGI9FVEZCEA5ZMtFwxS+LjMB8RTu+Roh0K26osODEw1wNtMVlBs5EPyTk8xwh69m1D8HoIxztKYS7KmnKi0mPhMW+MA2SlAORgc4AkM+gHwWRgqdidWlsZGVyH6J3Zx8BxCA9TtGJtjOhSH/HOt+w1bjpDCDwv1q6InCehjddAvn4dw==,fm2_lJPETous+NbaU5rpbiONGI9FVEZCEA5ZMtFwxS+LjMB8RTu+Roh0K26osODEw1wNtMVlBs5EPyTk8xwh69m1D8HoIxztKYS7KmnKi0mPhMW+MMQQLGB0opaNo0COZ3P4GUekLMO5aHR0cHM6Ly9hcGkuZmx5LmlvL2FhYS92MZgEks5o2hW0zo5yG9IXzgAQ89YKkc4AEPPWDMQQzDk7C1vwk9BDo/eA5V6UC8Qg33l1RdB2vPfVX0hsYVQFBsdvGBSiVg0tz1Vpz0HyigM='

echo "Repository: $REPO"
echo "Secret Name: $SECRET_NAME"
echo ""

# Confirm before proceeding
read -p "Do you want to add the Fly.io deploy token as a GitHub secret? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Adding secret to GitHub repository..."
    
    # Add the secret using gh CLI
    echo "$FLY_TOKEN" | gh secret set "$SECRET_NAME" --repo "$REPO"
    
    if [ $? -eq 0 ]; then
        echo "✅ Secret successfully added!"
        echo ""
        echo "The automatic deployment is now configured!"
        echo "Next push to master branch will trigger deployment."
        echo ""
        echo "You can verify the secret at:"
        echo "https://github.com/$REPO/settings/secrets/actions"
    else
        echo "❌ Failed to add secret. Please check your permissions and try again."
        exit 1
    fi
else
    echo "Operation cancelled."
    echo ""
    echo "To add the secret manually:"
    echo "1. Go to: https://github.com/$REPO/settings/secrets/actions"
    echo "2. Click 'New repository secret'"
    echo "3. Name: $SECRET_NAME"
    echo "4. Value: (copy the token from this script)"
fi

echo ""
echo "=================================="
echo "Additional Commands:"
echo "=================================="
echo ""
echo "List all secrets:"
echo "  gh secret list --repo $REPO"
echo ""
echo "Remove the secret (if needed):"
echo "  gh secret remove $SECRET_NAME --repo $REPO"
echo ""
echo "Trigger manual deployment:"
echo "  gh workflow run deploy.yml --repo $REPO"
echo ""
echo "View workflow runs:"
echo "  gh run list --repo $REPO"
echo ""