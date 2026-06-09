aspects = {
    "financial": "Concerns money, assets, investments, costs, revenues, and economic value.",
    "economic": "Relates to markets, supply and demand, economic systems, and macro/microeconomic impact.",
    "commercial": "Involves business activities, trade, sales, marketing, and customer relationships.",
    "legal": "Pertains to laws, regulations, compliance, rights, and obligations.",
    "political": "Relates to governance, public policy, power structures, and political influence.",
    "social": "Concerns interactions between individuals or groups, communities, and societal structures.",
    "cultural": "Involves traditions, customs, beliefs, arts, and shared values of a group.",
    "ethical": "Relates to moral principles, values, and judgments about right and wrong.",
    "health": "Concerns physical and mental health, medicine, healthcare systems, and well-being.",
    "psychological": "Relates to emotions, cognition, behavior, and mental processes.",
    "personal": "Pertains to individual life, identity, preferences, and personal experiences.",
    "educational": "Concerns learning, knowledge acquisition, teaching, and intellectual development.",
    "technological": "Relates to tools, systems, innovation, and technical infrastructure.",
    "environmental": "Concerns nature, ecosystems, sustainability, and environmental impact.",
    "scientific": "Relates to empirical research, theories, and systematic study of the natural world.",
    "historical": "Pertains to past events, timelines, and historical context.",
    "geographical": "Relates to location, physical space, regions, and spatial relationships.",
    "organizational": "Concerns structures, hierarchies, roles, and processes within organizations.",
    "operational": "Relates to processes, workflows, execution, and day-to-day functioning.",
    "strategic": "Concerns long-term planning, goals, positioning, and decision-making direction.",
    "security": "Concerns safety, risk, protection, and threat management (physical or digital).",
    "informational": "Relates to data, knowledge representation, communication, and information flow.",
    "logistical": "Concerns resources, transportation, coordination, and supply chains.",
    "demographic": "Relates to population characteristics such as age, gender, income, and distribution.",
    "spiritual": "Concerns beliefs, meaning, purpose, and existential or religious dimensions."
}

def render_aspects_sorted() -> str:
    return "\n".join(
        f"{key.capitalize()}: {aspects[key]}"
        for key in sorted(aspects.keys())
    )