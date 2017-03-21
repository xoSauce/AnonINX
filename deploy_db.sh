git commit -am "deploying to db automatically"
git push
fab db_1_2 $1
