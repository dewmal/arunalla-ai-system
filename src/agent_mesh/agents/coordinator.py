from ceylonai_next import LlmAgent

coordinator = LlmAgent("Coordinator", "google::gemini-2.5-flash")
coordinator.with_system_prompt(
    "You are a helpful coordinator. and we need output as a simple text"
)
coordinator.build()
