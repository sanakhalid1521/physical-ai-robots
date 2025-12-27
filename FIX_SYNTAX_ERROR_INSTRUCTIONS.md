# Fix for Vercel Deployment Error

## Problem
The Vercel deployment is failing due to a syntax error in src/components/ChatWindow.tsx at line 79.

## Error
Line 79 currently has:
```
     t backendUrl = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
```

## Solution
Replace line 79 with:
```
      const backendUrl = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
```

## Complete corrected section (lines 77-82):
```typescript
    try {
      // Use appropriate backend URL based on environment
      const backendUrl = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
        ? 'https://sanakhalid123-physicalairag.hf.space'  // Your Hugging Face deployment
        : 'http://localhost:8000';  // Local development
      const apiUrl = `${backendUrl}/api/rag/query`;
```

## Steps to fix:
1. Open src/components/ChatWindow.tsx
2. Find line 79 and replace `t backendUrl =` with `const backendUrl =`
3. Make sure the indentation is correct (should be 6 spaces)
4. Save the file
5. Commit and push:
```bash
git add src/components/ChatWindow.tsx
git commit -m "Fix syntax error in ChatWindow.tsx"
git push origin 001-ai-k12-efficiency-paper
```

This will fix the syntax error and allow Vercel to build successfully.