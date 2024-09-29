#!/bin/bash

# .env ファイルの読み込み
if [ -f .env ]; then
    export $(cat .env |grep -v '^#'| xargs)
fi

# ヘッダーとペイロードの生成
header='{
  "alg": "RS256",
  "typ": "JWT"
}'
payload="{
  \"iat\": $(date +%s),
  \"exp\": $(($(date +%s) + 600)),
  \"iss\": \"${GITHUB_APP_ID}\"
}"

# ヘッダーとペイロードをBase64エンコード
header_base64=$(echo -n "$header" | openssl base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n')
payload_base64=$(echo -n "$payload" | openssl base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n')

# 署名
signing_input="$header_base64.$payload_base64"
signature=$(echo -n "$signing_input" | openssl dgst -sha256 -sign "${GITHUB_APP_PRIVATE_KEY_PATH}" | openssl base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n')

# JWT組み立て
jwt="$signing_input.$signature"
# echo "${jwt}"

# RES=$(curl -X POST -s -o /dev/null \
RES=$(curl -X POST -s  \
  -H "Authorization: Bearer ${jwt}" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/app/installations/54986641/access_tokens)
# echo ${RES}

GITHUB_TOKEN=$(echo "${RES}" | grep -o '"token": *"[^"]*' | sed 's/"token": *"//')
# echo ${GITHUB_TOKEN}
git config --global url."https://x-access-token:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
if [ ! -d schema ]; then
  git submodule add https://github.com/TimeTutor-for-Discord/time_tutor.schema.git schema
fi
git submodule update --init --recursive --remote --rebase
# git submodule update --remote --rebase
# cat ~/.gitconfig
git config --global --unset url."https://x-access-token:${GITHUB_TOKEN}@github.com/".insteadOf 
