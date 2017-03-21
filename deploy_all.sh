echo "DEPLOY METHOD $1" 
git commit -am "deploying to all automatically"
git push
fab all_hosts $1
