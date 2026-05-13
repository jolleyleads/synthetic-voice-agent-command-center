\# Architecture Diagram



```mermaid

flowchart TD

&#x20;   A\[User Voice Command] --> B\[Browser Speech Recognition]

&#x20;   B --> C\[Flask Agent Backend]

&#x20;   C --> D\[OpenAI Reasoning Layer]

&#x20;   D --> E\[Tool Router]

&#x20;   E --> F\[AI Ops Jobs API]

&#x20;   E --> G\[Email Assistant API]

&#x20;   E --> H\[Workflow Events API]

&#x20;   F --> I\[Agent Response]

&#x20;   G --> I

&#x20;   H --> I

&#x20;   I --> J\[Browser Text-to-Speech Voice Reply]

```

