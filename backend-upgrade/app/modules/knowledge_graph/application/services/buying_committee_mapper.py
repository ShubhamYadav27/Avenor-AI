"""
Buying Committee Mapper (Phase 6.4)
Maps key decision makers into champions, economic buyers, technical evaluators, and blockers.
"""
from typing import List

from app.modules.knowledge_graph.domain.graph_entities import BuyingCommitteeMap, GraphNode


class BuyingCommitteeMapper:
    def map_committee(self, company_id: str, contacts: List[GraphNode]) -> BuyingCommitteeMap:
        champions = [c for c in contacts if "VP" in c.properties.get("title", "") or "Head" in c.properties.get("title", "")]
        economic = [c for c in contacts if "CFO" in c.properties.get("title", "") or "Finance" in c.properties.get("title", "")]
        technical = [c for c in contacts if "CTO" in c.properties.get("title", "") or "Engineer" in c.properties.get("title", "")]
        blockers = [c for c in contacts if "Procurement" in c.properties.get("title", "")]

        if not champions and contacts:
            champions = [contacts[0]]

        total = len(champions) + len(economic) + len(technical) + len(blockers)

        return BuyingCommitteeMap(
            company_id=company_id,
            champions=champions,
            economic_buyers=economic,
            technical_evaluators=technical,
            blockers=blockers,
            total_members=total,
        )


buying_committee_mapper = BuyingCommitteeMapper()
