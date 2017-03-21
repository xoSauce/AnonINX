echo "DEPLOY METHOD $1" 
git commit -am "deploying to all automatically"
git push
fab debug_hosts $1
