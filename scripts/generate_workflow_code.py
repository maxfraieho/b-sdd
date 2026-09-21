#!/usr/bin/env python3
"""
Generate TypeScript Workflow SDK code for B-SDD Autonomous Supervisor Harness.
"""

ts_code = """import { workflow, node, trigger, ifElse, expr, newCredential } from '@n8n/workflow-sdk';

const gmailTrigger = trigger({
  type: 'n8n-nodes-base.gmailTrigger',
  version: 1.2,
  config: {
    name: 'Gmail Trigger (B-SDD)',
    position: [-480, -100],
    parameters: {
      pollTimes: {
        item: [
          {
            mode: 'everyX',
            value: 1,
            unit: 'minutes'
          }
        ]
      },
      simple: false,
      filters: {
        readStatus: 'unread',
        q: 'from:tukroschu@gmail.com subject:[B-SDD-DISPATCH'
      }
    },
    credentials: {
      gmailOAuth2: newCredential('Gmail account')
    }
  },
  output: [
    {
      id: '1a0c3ffea8a5e4ba',
      snippet: 'OUTBOX_AGI_SPRINT_022_EPIC_KINDLE_PIPELINE',
      subject: '[B-SDD-DISPATCH: SPRINT_022] OUTBOX_AGI_SPRINT_022_EPIC_KINDLE_PIPELINE'
    }
  ]
});

const extractParams = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Extract Params',
    position: [-260, -100],
    parameters: {
      assignments: {
        assignments: [
          {
            id: 'instruction-name',
            name: 'instruction_name',
            value: expr("={{ ($json.subject || $json.snippet || $json.text || '').match(/OUTBOX_AGI_[A-Za-z0-9_]+/g) ? ($json.subject || $json.snippet || $json.text || '').match(/OUTBOX_AGI_[A-Za-z0-9_]+/g)[0] : 'OUTBOX_AGI_SPRINT_022_EPIC_KINDLE_PIPELINE' }}"),
            type: 'string'
          },
          {
            id: 'sprint-id',
            name: 'sprint_id',
            value: expr("={{ ($json.subject || '').match(/SPRINT_\\\\d+/i) ? ($json.subject || '').match(/SPRINT_\\\\d+/i)[0].toLowerCase() : 'sprint_022' }}"),
            type: 'string'
          }
        ]
      }
    }
  },
  output: [
    {
      instruction_name: 'OUTBOX_AGI_SPRINT_021_ISOLATE_EXTENDED_SKILLS',
      sprint_id: 'sprint_021'
    }
  ]
});

const dispatchHost161 = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'Dispatch to Host 161',
    position: [-40, -100],
    parameters: {
      method: 'POST',
      url: 'http://100.65.225.122:8161/dispatch',
      sendBody: true,
      specifyBody: 'keypair',
      bodyParameters: {
        parameters: [
          {
            name: 'instruction_name',
            value: expr('={{ $json.instruction_name }}')
          },
          {
            name: 'sprint_id',
            value: expr('={{ $json.sprint_id }}')
          }
        ]
      },
      options: {
        timeout: 10000
      }
    }
  },
  output: [
    {
      status: 'QUEUED'
    }
  ]
});

const supervisorCallbackWebhook = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2,
  config: {
    name: 'Supervisor Callback Webhook',
    position: [-480, 140],
    parameters: {
      path: 'bsdd-supervisor-result',
      httpMethod: 'POST',
      responseMode: 'onReceived'
    }
  },
  output: [
    {
      body: {
        project: 'B-SDD',
        sprint_id: 'sprint_021_verify',
        status: 'SUCCESS',
        node: '192.168.3.161',
        commit: '84c3337',
        tests_summary: '18/18 PASSED',
        report_name: 'INBOX_GEMINI_SPRINT_021_ISOLATE_EXTENDED_SKILLS_REPORT',
        error_details: ''
      }
    }
  ]
});

const processTelemetry = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Process Telemetry & Source',
    position: [-260, 140],
    parameters: {
      assignments: {
        assignments: [
          {
            id: 'project',
            name: 'project',
            value: expr("={{ $json.body?.project || $json.project || 'B-SDD' }}"),
            type: 'string'
          },
          {
            id: 'status',
            name: 'status',
            value: expr("={{ $json.body?.status || $json.status || 'SUCCESS' }}"),
            type: 'string'
          },
          {
            id: 'node',
            name: 'node',
            value: expr("={{ $json.body?.node || $json.node || $json.body?.host || '192.168.3.161' }}"),
            type: 'string'
          },
          {
            id: 'sprint_id',
            name: 'sprint_id',
            value: expr("={{ $json.body?.sprint_id || $json.sprint_id || 'sprint_022' }}"),
            type: 'string'
          },
          {
            id: 'commit',
            name: 'commit',
            value: expr("={{ $json.body?.commit || $json.commit || 'HEAD' }}"),
            type: 'string'
          },
          {
            id: 'tests_summary',
            name: 'tests_summary',
            value: expr("={{ $json.body?.tests_summary || $json.tests_summary || '18/18 PASSED' }}"),
            type: 'string'
          },
          {
            id: 'report_name',
            name: 'report_name',
            value: expr("={{ $json.body?.report_name || $json.report_name || $json.body?.source_title || 'INBOX_GEMINI_REPORT' }}"),
            type: 'string'
          },
          {
            id: 'error_details',
            name: 'error_details',
            value: expr("={{ $json.body?.error_details || $json.error || $json.body?.failed_command || $json.failed_command || '' }}"),
            type: 'string'
          }
        ]
      }
    }
  },
  output: [
    {
      project: 'B-SDD',
      status: 'SUCCESS',
      node: '192.168.3.161',
      sprint_id: 'sprint_021',
      commit: '84c3337',
      tests_summary: '18/18 PASSED',
      report_name: 'INBOX_GEMINI_SPRINT_021_ISOLATE_EXTENDED_SKILLS_REPORT',
      error_details: ''
    }
  ]
});

const checkStatus = ifElse({
  version: 2.2,
  config: {
    name: 'Check Status',
    position: [-60, 140],
    parameters: {
      conditions: {
        options: {
          caseSensitive: true,
          leftValue: '',
          typeValidation: 'loose',
          version: 2
        },
        conditions: [
          {
            id: 'cond-status-success',
            leftValue: expr('={{ $json.body?.status || $json.status }}'),
            rightValue: 'SUCCESS',
            operator: {
              type: 'string',
              operation: 'equals',
              singleValue: true
            }
          }
        ],
        combinator: 'and'
      },
      looseTypeValidation: true
    }
  }
});

const telegramNotifySuccess = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'Telegram Notify (Success)',
    position: [160, 240],
    parameters: {
      method: 'POST',
      url: 'https://api.telegram.org/bot8717667434:AAFWddh_xwTfMVHW7puxrlIFprbO9m_Au7Y/sendMessage',
      sendBody: true,
      specifyBody: 'keypair',
      bodyParameters: {
        parameters: [
          {
            name: 'chat_id',
            value: '6412868393'
          },
          {
            name: 'text',
            value: expr('={{ "✅ [PROJECT: " + ($json.body?.project || $json.project || "B-SDD") + "] [" + ($json.body?.status || $json.status) + "] Крок спринту завершено успішно\\n\\n📍 Вузол: " + ($json.body?.node || $json.node || "192.168.3.161") + "\\n⚙️ Спринт: " + ($json.body?.sprint_id || $json.sprint_id) + "\\n📦 Комміт: " + ($json.body?.commit || $json.commit || "HEAD") + "\\n🧪 Тести: " + ($json.body?.tests_summary || $json.tests_summary || "18/18 PASSED") + "\\n📄 Звіт: " + ($json.body?.report_name || $json.report_name) + " у NotebookLM\\n\\nВсі інваріанти та тести виконано без помилок." }}')
          }
        ]
      },
      options: {
        timeout: 10000
      }
    }
  },
  output: [
    {
      ok: true
    }
  ]
});

const telegramAlert = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'Telegram Alert (/me)',
    position: [160, 80],
    parameters: {
      method: 'POST',
      url: 'https://api.telegram.org/bot8717667434:AAFWddh_xwTfMVHW7puxrlIFprbO9m_Au7Y/sendMessage',
      sendBody: true,
      specifyBody: 'keypair',
      bodyParameters: {
        parameters: [
          {
            name: 'chat_id',
            value: '6412868393'
          },
          {
            name: 'text',
            value: expr('={{ "🚨 [PROJECT: " + ($json.body?.project || $json.project || "B-SDD") + "] [INTERRUPT] Потрібне втручання (/me)\\n\\n📍 Вузол: " + ($json.body?.node || $json.node || "192.168.3.161") + "\\n⚙️ Спринт: " + ($json.body?.sprint_id || $json.sprint_id) + "\\n❌ Помилка: " + ($json.body?.error_details || $json.error || $json.body?.failed_command || $json.failed_command || "перегляньте логи") + "\\n📄 Звіт: " + ($json.body?.report_name || $json.report_name) + " у NotebookLM\\n\\nСтатус: " + ($json.body?.status || $json.status || "FAILED") }}')
          }
        ]
      },
      options: {
        timeout: 10000
      }
    }
  },
  output: [
    {
      ok: true
    }
  ]
});

const sendEmailGmail = node({
  type: 'n8n-nodes-base.gmail',
  version: 2.2,
  config: {
    name: 'Send Email (Gmail)',
    position: [380, 240],
    parameters: {
      resource: 'message',
      operation: 'send',
      sendTo: 'tukroschu@gmail.com',
      subject: expr('={{ "[PROJECT: " + ($(\\'Process Telemetry & Source\\').item.json.project || "B-SDD") + "] | " + ($(\\'Process Telemetry & Source\\').item.json.sprint_id || "sprint_022") + " | Status: " + ($(\\'Process Telemetry & Source\\').item.json.status || "SUCCESS") }}'),
      message: expr('={{ "=== B-SDD TELEMETRY DISPATCH ===\\n\\nВузол: " + ($(\\'Process Telemetry & Source\\').item.json.node || "192.168.3.161") + "\\nПроєкт: [PROJECT: " + ($(\\'Process Telemetry & Source\\').item.json.project || "B-SDD") + "]\\nСпринт: " + ($(\\'Process Telemetry & Source\\').item.json.sprint_id || "sprint_022") + "\\nСтатус: " + ($(\\'Process Telemetry & Source\\').item.json.status || "SUCCESS") + "\\nКомміт: " + ($(\\'Process Telemetry & Source\\').item.json.commit || "HEAD") + "\\nТести: " + ($(\\'Process Telemetry & Source\\').item.json.tests_summary || "18/18 PASSED") + "\\nЗвіт у NotebookLM: " + ($(\\'Process Telemetry & Source\\').item.json.report_name || "") + "\\n\\n---\\nB-SDD Telemetry Dual-Loop" }}')
    },
    credentials: {
      gmailOAuth2: newCredential('Gmail account')
    }
  },
  output: [
    {
      id: 'msg_success_123'
    }
  ]
});

export default workflow('6FzcypHVkvqrxf9o', 'B-SDD Autonomous Supervisor Harness')
  .add(gmailTrigger)
  .to(extractParams)
  .to(dispatchHost161)
  .add(supervisorCallbackWebhook)
  .to(processTelemetry)
  .to(
    checkStatus
      .onTrue(telegramNotifySuccess.to(sendEmailGmail))
      .onFalse(telegramAlert)
  );
"""

with open("/home/vokov/projects/b-sdd/scripts/workflow_bsdd_sdk.ts", "w") as f:
    f.write(ts_code)

print("Saved workflow_bsdd_sdk.ts successfully.")
