#!/bin/bash

BLUE='\033[0;34m'
NC='\033[0m' # No Color

#cd burgers

source venv/bin/activate

echo -e "${BLUE}Updating repo${NC}"
git pull


echo -e "${BLUE}Collecting packages${NC}"
pip3 install -r requirements.txt

echo -e "${BLUE}Collecting static${NC}"
venv/bin/python3 manage.py collectstatic --noinput

python3 manage.py migrate


echo -e "${BLUE}Restarting servers${NC}"
systemctl stop burgers

systemctl daemon-reload

systemctl start burgers

git_commit=$(git rev-parse HEAD)

curl -H "X-Rollbar-Access-Token: d945324a58034cfa956594309698eac1" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' \
 -d '{"environment":"production", "revision": "$git_commit", "rollbar_username": "vladmarchenkosteam",  "status": "succeeded"}'


npm install
echo -e "${BLUE}Building JS${NC}"
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
