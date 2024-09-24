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

RES=$(curl -X POST -s -o /dev/null \
  -H "Authorization: Bearer ${jwt}" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/app/installations/54986641/access_tokens)
# echo ${RES}

GITHUB_TOKEN=$(echo "${RES}" | grep -o '"token": *"[^"]*' | sed 's/"token": *"//')
git config --global url."https://x-access-token:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
git submodule update --init --recursive
# git submodule update --remote --rebase #これを実行するにはGitHub App側の権限が不足していそうだが詳細は未確認
