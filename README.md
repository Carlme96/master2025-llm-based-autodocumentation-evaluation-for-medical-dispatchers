# master2025-llm-based-autodocumentation-evaluation-for-medical-dispatchers

Repository for LLM Based Autodocumentation and Evaluation of Medical Emergency Dispatcher Conversations

**Authors** \
Carl Magnus Elvevold \
Truc Erik Truong

# Instructions

## Folder structure

```
.
├── app/
│   ├── modules/
│   │   ├── evaluateBot/
│   │   │   ├── evaluateBot.py
│   │   │   └── ...
│   │   ├── generateReport/
│   │   │   └── generateReport.py
│   │   ├── summaryBot/
│   │   │   ├── summaryBot.py
│   │   │   └── ...
│   │   └── basedata.py
│   ├── routers/
│   │   └── <Router files>
│   ├── ragStuff/
│   │   ├── LabelWork/
│   │   │   └── <Norwegian index md files>
│   │   └── VectorStores/
│   ├── config.py
│   ├── main.py
│   ├── .env.template
│   ├── .env
│   └── <other config files>
├── reportgenerator/
│   └── <Frontend files>
├── FineTuning/
│   └── <Fine tuning setup>
├── compose.yaml
└── README.md
```

## Setup application
1. This project is is using the 'uv' python package manager. [Install here](https://github.com/astral-sh/uv)
1. In the `app/` folder, run `uv sync`.
1. Create a `.env` file, and add all configuration needed. See `.env.template`.
1. Make sure you have `node` and `npm` installed. In the `reportgenerator/` folder, run `npm i`.
1. Run `docker compose up`. It may need additional packages depending on your system. In that case, install them with `uv add <package name>` in the `app/` folder.
1. The frontend application should be available at `localhost:3000`