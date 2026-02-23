#!/bin/bash

# Paper Submitter - 提交 HF 论文到 aipaper.cc 进行精读
# 用法: ./script.sh <hf_paper_id>
# 示例: ./script.sh 2601.12345

cd "$(dirname "$0")"

if [ $# -lt 1 ]; then
    echo "❌ 用法: ./script.sh <hf_paper_id>"
    echo "   示例: ./script.sh 2601.12345"
    exit 1
fi

python3 submitter.py "$1"
