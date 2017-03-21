echo "DEPLOY METHOD $1" 
git commit -am "deploying to db automatically"
git push
fab debug_hosts $1
