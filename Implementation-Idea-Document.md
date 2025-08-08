# AI Research Agent - Implementation Idea Document

## Project Overview

**Goal**: Build a cost-effective AI research agent platform that performs strategic business analysis for Crane using established frameworks (Porter's Five Forces, PESTEL, SWOT, Ansoff) with complete observability and multi-agent extensibility.

**Budget**: $20/month, targeting ~$6/month actual usage
**Timeline**: 8-week development phases
**Output**: Detailed markdown reports for strategic analysis

---

## 1. Research Logic Clarification

### 1.1 Prerequisites: Crane Positioning Document

**TASK**: Create comprehensive positioning document for Crane before starting research agent

**Positioning Document Requirements**:
- **Product Overview**: Detailed description of each Crane component (Material Manager, Submittal Viewer, Project Schedule, Delivery Portal, Multi-agent System)
- **Value Propositions**: Core value delivered by each component
- **Target Customers**: Detailed personas (General Contractors, Subcontractors, Project Managers, Suppliers)
- **Key Differentiators**: What makes Crane unique vs. existing solutions
- **Technology Approach**: AI/ML capabilities, integration philosophy, data approach
- **Market Positioning**: How Crane fits in the construction tech landscape
- **Success Metrics**: How Crane measures value delivery for customers

**Usage**: This document will be input for SWOT analysis strengths and value proposition mapping

---

### 1.2 Trusted Sources Catalog (Authoritative Feeds to Use)

- Academic journals (construction + applied AI):
  - [Automation in Construction (Elsevier)](https://www.sciencedirect.com/journal/automation-in-construction)
  - [Construction Management and Economics (Taylor & Francis)](https://www.tandfonline.com/journals/rcme20)
  - [Advanced Engineering Informatics (Elsevier)](https://www.sciencedirect.com/journal/advanced-engineering-informatics)
  - [ASCE Journal of Construction Engineering and Management](https://ascelibrary.org/journal/jcemd4)
  - [ASCE Journal of Computing in Civil Engineering](https://ascelibrary.org/journal/jcdenp)
  - [ITcon – Journal of Information Technology in Construction](https://www.itcon.org/)

- Construction tech publications/newsletters:
  - [Construction Dive](https://www.constructiondive.com/)
  - [ENR – Engineering News‑Record](https://www.enr.com/)
  - [Building Design+Construction (BDC)](https://www.bdcnetwork.com/)
  - [BuiltWorlds](https://builtworlds.com/)
  - [AECbytes](https://aecbytes.com/)
  - [The ConTechCrew](https://thecontechcrew.com/)
  - [Construction Physics (Brian Potter)](https://constructionphysics.substack.com/)

- AI/tech trend newsletters (macro + AI direction):
  - [MIT Technology Review – The Algorithm](https://www.technologyreview.com/newsletter-preferences/)
  - [DeepLearning.AI – The Batch](https://www.deeplearning.ai/the-batch/about/)
  - [Import AI – Jack Clark](https://importai.substack.com/)
  - [Air Street – Your Guide to AI](https://press.airstreet.com/)
  - [Ben’s Bites](https://www.bensbites.co/)
  - [TLDR AI](https://tldr.tech/ai)
  - [Context Engineering](https://www.context.engineering/) (emerging prompting/agents topics)

- LinkedIn/Twitter influencer watchlist (construction tech + AI in AEC):
  - James Benham (JBKnowledge / ConTech) – practical ConTech adoption
  - Jeff Sample (The ConTechCrew) – workflows, field ops, integrations
  - Brian Potter (Construction Physics) – deep structural analysis of construction
  - Salla Palos (AEC digital transformation) – enterprise AEC innovation
  - Anthony Hauck (Hypar) – computational design + platforms in AEC
  - Randy Deutsch (Illinois Architecture) – AEC + AI design discourse
  - Phil Read (AEC) – BIM/authoring tools ecosystem

Note: These are seed sources; the agent will keep a local watchlist that you can edit.

### 1.3 Source Weighting & Citation Policy

- Evidence weighting (default target mix per section):
  - Academic journals: 30%
  - Credible industry publications/newsletters: 35%
  - Primary sources (company sites, financials, filings): 25%
  - Social/influencers (thought leadership): 10% (used for hypotheses, not facts)

- Freshness requirements:
  - Newsletters/industry: last 6–12 months preferred
  - Academic: last 3–5 years unless a seminal paper
  - Company/product info: current pages or docs with date or commit/version

- Citation policy (enforced in outputs):
  - Every claim must include inline citations with: title, outlet, URL, author, published_date, source_type
  - Minimum 5 citations per major section, including ≥2 industry and ≥1 academic where applicable
  - Include a "confidence" score per claim tied to source mix, recency, and corroboration count

### Core Research Workflow

#### Phase 1: Competitive Analysis (Porter's Five Forces)
```python
async def competitive_analysis_with_porters(components: List[str], positioning_doc: dict) -> CompetitiveAnalysisResults:
    """
    Combined competitor discovery and Porter's Five Forces analysis
    
    Process:
    1. For each component: Run 3 deep research queries for competitor discovery
    2. Apply Porter's Five Forces analysis per component and overall
    3. Synthesize competitive intelligence with strategic framework
    4. Return comprehensive competitive analysis
    
    Scope:
    - Component-level analysis: Each Crane component vs its specific competitors
    - Overall analysis: Crane as a platform vs construction tech ecosystem
    """
    component_analyses: List[ComponentCompetitorAnalysis] = []

    for component in components:
        component_description = extract_component_description(positioning_doc, component)

        research_queries = {
            "competitor_identification": {
                "query": (
                    f"Identify the top 5 direct competitors and top 3 partial competitors to the following solution in construction software. "
                    f"Solution name: '{component}'. Solution description: '{component_description}'. "
                    f"Focus on companies serving general contractors, subcontractors, and project managers. "
                    f"Include funding status, company size, and primary target market."
                ),
                "output_structure": {
                    "direct_competitors": [
                        {
                            "company": "string",
                            "product": "string",
                            "target_audience": "string",
                            "funding": "string",
                            "company_size": "string",
                            "market_focus": "string"
                        }
                    ],
                    "partial_competitors": [
                        {
                            "company": "string",
                            "product": "string",
                            "overlap_area": "string",
                            "differentiation": "string"
                        }
                    ],
                    "citations": [
                        {"title": "string", "url": "string", "outlet": "string", "author": "string", "published_date": "string", "source_type": "string"}
                    ]
                }
            },
            "market_landscape": {
                "query": (
                    f"Analyze the competitive market landscape for the following solution in construction technology. "
                    f"Solution name: '{component}'. Solution description: '{component_description}'. "
                    f"Include market size/growth, recent funding rounds, AI/ML usage, and positioning strategies of key players."
                ),
                "output_structure": {
                    "market_overview": {
                        "market_size": "string",
                        "growth_rate": "string",
                        "key_trends": ["string"]
                    },
                    "competitive_dynamics": [
                        {
                            "company": "string",
                            "market_position": "string",
                            "recent_funding": "string",
                            "technology_approach": "string",
                            "competitive_advantage": "string"
                        }
                    ],
                    "citations": [
                        {"title": "string", "url": "string", "outlet": "string", "author": "string", "published_date": "string", "source_type": "string"}
                    ]
                }
            },
            "feature_positioning": {
                "query": (
                    f"Compare feature sets, pricing models, and positioning strategies of leading platforms for the following solution in construction. "
                    f"Solution name: '{component}'. Solution description: '{component_description}'. "
                    f"Focus on differentiators, target segments, integrations, and UX approaches."
                ),
                "output_structure": {
                    "feature_comparison": [
                        {
                            "company": "string",
                            "core_features": ["string"],
                            "pricing_model": "string",
                            "target_segments": ["string"],
                            "integrations": ["string"],
                            "key_differentiators": ["string"]
                        }
                    ],
                    "positioning_insights": {
                        "premium_players": ["string"],
                        "cost_effective_solutions": ["string"],
                        "niche_specialists": ["string"]
                    },
                    "citations": [
                        {"title": "string", "url": "string", "outlet": "string", "author": "string", "published_date": "string", "source_type": "string"}
                    ]
                }
            }
        }

        research_tasks = []
        for query_type, query_config in research_queries.items():
            task = execute_deep_research(
                query=query_config["query"],
                expected_structure=query_config["output_structure"],
                research_api="perplexity-deep-research",
                context_data={
                    "component": component,
                    "component_description": component_description,
                    "trusted_sources_policy": "Use journals, AEC publications, primary company pages; include citations"
                }
            )
            research_tasks.append((query_type, task))

        research_results = {}
        for query_type, task in research_tasks:
            research_results[query_type] = await task

        component_analysis = await synthesize_competitor_analysis(component, research_results)
        component_analyses.append(component_analysis)

    porters_analysis = await apply_porters_five_forces(component_analyses)

    return CompetitiveAnalysisResults(
        component_analyses=component_analyses,
        porters_five_forces=porters_analysis,
        analysis_timestamp=datetime.utcnow()
    )

async def apply_porters_five_forces(component_analyses: List[ComponentCompetitorAnalysis]) -> PortersFiveForces:
    """
    Apply Porter's Five Forces framework to competitive data
    
    Analysis Levels:
    1. Per-component analysis (each Crane feature vs its competitors)
    2. Overall platform analysis (Crane vs construction tech ecosystem)
    """
    
    # Component-level Porter's analysis
    component_forces = {}
    for analysis in component_analyses:
        component_forces[analysis.component] = await analyze_component_forces(analysis)
    
    # Overall platform Porter's analysis  
    overall_forces = await analyze_overall_platform_forces(component_analyses)
    
    return PortersFiveForces(
        component_level=component_forces,
        overall_platform=overall_forces,
        strategic_insights=await generate_porters_insights(component_forces, overall_forces)
    )

async def analyze_component_forces(analysis: ComponentCompetitorAnalysis) -> ComponentPortersForces:
    """
    Analyze Porter's Five Forces for specific component
    """
    
    forces_analysis = {
        "competitive_rivalry": {
            "query": f"Analyze competitive rivalry intensity for {analysis.component} in construction software. Consider number of competitors, market growth, product differentiation, switching costs, and competitive moves.",
            "factors": ["competitor_count", "market_growth", "differentiation_level", "switching_costs", "price_competition"]
        },
        "threat_of_new_entrants": {
            "query": f"Assess threat of new entrants in {analysis.component} construction software market. Consider barriers to entry, capital requirements, customer acquisition costs, and technology barriers.",
            "factors": ["entry_barriers", "capital_requirements", "customer_acquisition", "technology_barriers", "regulatory_barriers"]
        },
        "bargaining_power_suppliers": {
            "query": f"Evaluate supplier power for {analysis.component} solutions. Consider technology vendors, data providers, integration partners, and specialized talent requirements.",
            "factors": ["supplier_concentration", "switching_costs", "substitute_inputs", "supplier_differentiation"]
        },
        "bargaining_power_buyers": {
            "query": f"Analyze buyer power for {analysis.component} targeting GCs and subcontractors. Consider customer concentration, price sensitivity, switching costs, and alternative solutions.",
            "factors": ["customer_concentration", "price_sensitivity", "switching_costs", "buyer_information", "substitute_availability"]
        },
        "threat_of_substitutes": {
            "query": f"Assess substitute threats for {analysis.component}. Consider manual processes, alternative technologies, and indirect solutions that address same customer needs.",
            "factors": ["substitute_performance", "switching_costs", "buyer_propensity", "price_performance"]
        }
    }
    
    # Execute Porter's analysis research
    forces_results = {}
    for force_name, force_config in forces_analysis.items():
        force_result = await execute_deep_research(
            query=force_config["query"],
            expected_structure={
                "force_intensity": "string",  # High/Medium/Low
                "key_factors": ["string"],
                "specific_examples": ["string"],
                "strategic_implications": ["string"],
                "score": "integer"  # 1-5 scale
            },
            research_api="perplexity-deep-research"
        )
        forces_results[force_name] = force_result
    
    return ComponentPortersForces(
        component=analysis.component,
        forces=forces_results,
        overall_attractiveness=calculate_market_attractiveness(forces_results)
    )

async def execute_deep_research(query: str, expected_structure: dict, research_api: str, context_data: Optional[dict] = None) -> dict:
    """
    Execute structured deep research using research APIs
    """
    
    # System prompt for structured output
    system_prompt = f"""
    You are a business research analyst conducting competitive intelligence research.
    
    Your task: {query}
    
    CRITICAL: Your response must follow this exact JSON structure:
    {json.dumps(expected_structure, indent=2)}
    
    Research Guidelines:
    - Use only recent, verified information (last 12 months preferred)
    - Focus on construction industry context
    - Include specific data points (funding amounts, employee counts, etc.)
    - Distinguish between direct competitors (same product category) and partial competitors (adjacent solutions)
    - Prioritize companies serving GCs, subcontractors, and project managers
    - Cite all claims with title, outlet, url, author, published_date, source_type (academic, industry, primary, influencer)
    - Follow source weighting: Academic (30%), Industry (35%), Primary (25%), Influencers (10%)
    - Only include sources that can be verified online and prefer US-focused insights
    
    Context (if provided):
    {json.dumps(context_data or {}, indent=2)}
    
    Return ONLY valid JSON matching the required structure.
    """
    
    if research_api == "perplexity-deep-research":
        response = await perplexity_research_call(
            query=query,
            system_prompt=system_prompt,
            model="llama-3.1-sonar-large-128k-online"
        )
    elif research_api == "google-deep-research":
        response = await google_deep_research_call(
            query=query,
            system_prompt=system_prompt
        )
    else:
        # Fallback to OpenRouter with web search
        response = await openrouter_research_call(
            query=query,
            system_prompt=system_prompt,
            model="anthropic/claude-3.5-sonnet"
        )
    
    # Parse and validate JSON response
    try:
        structured_data = json.loads(response)
        validate_research_structure(structured_data, expected_structure)
        return structured_data
    except (json.JSONDecodeError, ValidationError) as e:
        # Retry with clarification if parsing fails
        return await retry_research_with_clarification(query, expected_structure, str(e))

async def synthesize_competitor_analysis(component: str, research_results: dict) -> ComponentCompetitorAnalysis:
    """
    Combine research results into final competitor analysis
    """
    
    # Extract competitors from all research
    all_competitors = {}
    
    # Add direct competitors
    for comp in research_results["competitor_identification"]["direct_competitors"]:
        comp_name = comp["company"]
        all_competitors[comp_name] = {
            "type": "direct",
            "basic_info": comp,
            "market_data": None,
            "feature_data": None
        }
    
    # Add partial competitors  
    for comp in research_results["competitor_identification"]["partial_competitors"]:
        comp_name = comp["company"]
        all_competitors[comp_name] = {
            "type": "partial", 
            "basic_info": comp,
            "market_data": None,
            "feature_data": None
        }
    
    # Enrich with market landscape data
    for comp_data in research_results["market_landscape"]["competitive_dynamics"]:
        comp_name = comp_data["company"]
        if comp_name in all_competitors:
            all_competitors[comp_name]["market_data"] = comp_data
    
    # Enrich with feature/positioning data
    for comp_data in research_results["feature_positioning"]["feature_comparison"]:
        comp_name = comp_data["company"]
        if comp_name in all_competitors:
            all_competitors[comp_name]["feature_data"] = comp_data
    
    # Rank and select top competitors
    ranked_competitors = await rank_competitors_by_relevance(all_competitors, component)
    
    return ComponentCompetitorAnalysis(
        component=component,
        direct_competitors=ranked_competitors["direct"][:3],  # Top 3 direct
        partial_competitors=ranked_competitors["partial"][:3],  # Top 3 partial
        market_overview=research_results["market_landscape"]["market_overview"],
        positioning_insights=research_results["feature_positioning"]["positioning_insights"],
        research_timestamp=datetime.utcnow(),
        research_sources=["perplexity-deep-research", "market-intelligence", "competitive-analysis"]
    )
```

#### Phase 2: Macro Environment Analysis (PESTEL)
```python
async def macro_environment_analysis() -> PESTELAnalysis:
    """
    Separate research focused on external macro environment using PESTEL framework
    
    Scope:
    - Construction industry in the U.S.
    - Technology adoption in construction
    - AI and technology adoption trends
    - Regulatory changes affecting construction software
    """
    
    pestel_research_queries = {
        "political": {
            "query": "Analyze political factors affecting construction technology in the U.S. Include government spending on infrastructure, construction regulations, trade policies, and political stability impacts on construction industry.",
            "focus_areas": ["infrastructure_spending", "regulatory_environment", "trade_policies", "political_stability"]
        },
        "economic": {
            "query": "Evaluate economic factors impacting construction technology adoption in the U.S. Include interest rates, construction market cycles, economic growth, inflation effects, and funding availability for construction tech.",
            "focus_areas": ["interest_rates", "market_cycles", "economic_growth", "construction_spending", "tech_investment"]
        },
        "social": {
            "query": "Assess social factors influencing construction technology adoption. Include workforce demographics, skill gaps, technology acceptance, safety culture, and generational changes in construction.",
            "focus_areas": ["workforce_demographics", "skill_gaps", "technology_acceptance", "safety_culture", "generational_shifts"]
        },
        "technological": {
            "query": "Analyze technological trends in construction and AI adoption. Include emerging technologies, AI/ML integration, automation trends, digital transformation, and technology infrastructure developments.",
            "focus_areas": ["ai_ml_adoption", "automation_trends", "digital_transformation", "emerging_technologies", "infrastructure_tech"]
        },
        "environmental": {
            "query": "Evaluate environmental factors affecting construction technology. Include sustainability requirements, green building standards, climate change impacts, environmental regulations, and ESG considerations.",
            "focus_areas": ["sustainability_requirements", "green_standards", "climate_impacts", "environmental_regulations", "esg_factors"]
        },
        "legal": {
            "query": "Analyze legal factors impacting construction software and AI adoption. Include data privacy regulations, AI governance, construction compliance requirements, liability issues, and intellectual property considerations.",
            "focus_areas": ["data_privacy", "ai_governance", "construction_compliance", "liability_issues", "ip_considerations"]
        }
    }
    
    # Execute PESTEL research in parallel
    pestel_results = {}
    for factor, config in pestel_research_queries.items():
        pestel_result = await execute_deep_research(
            query=config["query"],
            expected_structure={
                "factor_impact": "string",  # High/Medium/Low
                "current_trends": ["string"],
                "future_outlook": "string",
                "opportunities": ["string"],
                "threats": ["string"],
                "key_indicators": ["string"],
                "timeline": "string",  # Short-term/Medium-term/Long-term
                "impact_score": "integer"  # 1-5 scale
            },
            research_api="perplexity-deep-research"
        )
        pestel_results[factor] = pestel_result
    
    return PESTELAnalysis(
        factors=pestel_results,
        macro_insights=await generate_macro_insights(pestel_results),
        opportunities_threats=await extract_macro_opportunities_threats(pestel_results),
        analysis_timestamp=datetime.utcnow()
    )
```

#### Phase 3: Product-Market Analysis (SWOT)
```python
async def product_market_analysis(positioning_doc: dict, competitive_analysis: CompetitiveAnalysisResults, pestel_analysis: PESTELAnalysis) -> SWOTAnalysis:
    """
    Analyze Crane's product-market positioning using SWOT framework
    
    Data Sources:
    - Strengths: From positioning doc + competitive research insights
    - Weaknesses: From competitive gaps and analysis
    - Opportunities: From PESTEL analysis + market research
    - Threats: From Porter's analysis + PESTEL threats
    """
    
    swot_analysis = {
        "strengths": {
            "query": f"Based on Crane's positioning and competitive analysis, identify key strengths. Consider unique value propositions, technology advantages, market positioning, and competitive differentiators from the positioning document.",
            "data_sources": ["positioning_doc", "competitive_advantages", "technology_differentiators"],
            "input_data": {
                "positioning": positioning_doc,
                "competitive_insights": competitive_analysis.strategic_insights
            }
        },
        "weaknesses": {
            "query": "Identify Crane's potential weaknesses based on competitive gap analysis. Consider areas where competitors are stronger, missing features, market presence gaps, and resource constraints.",
            "data_sources": ["competitive_gaps", "feature_comparison", "market_presence"],
            "input_data": {
                "competitive_gaps": await extract_competitive_gaps(competitive_analysis),
                "market_position": competitive_analysis.market_overview
            }
        },
        "opportunities": {
            "query": "Identify market opportunities for Crane based on PESTEL analysis and market research. Consider market trends, technology adoption, regulatory changes, and unmet customer needs.",
            "data_sources": ["pestel_opportunities", "market_trends", "customer_needs"],
            "input_data": {
                "pestel_opportunities": pestel_analysis.opportunities_threats["opportunities"],
                "market_trends": pestel_analysis.factors
            }
        },
        "threats": {
            "query": "Identify threats to Crane based on competitive forces and macro environment. Consider competitive threats from Porter's analysis and external threats from PESTEL analysis.",
            "data_sources": ["porters_threats", "pestel_threats", "competitive_threats"],
            "input_data": {
                "competitive_threats": competitive_analysis.porters_five_forces.strategic_insights,
                "macro_threats": pestel_analysis.opportunities_threats["threats"]
            }
        }
    }
    
    # Execute SWOT analysis
    swot_results = {}
    for swot_element, config in swot_analysis.items():
        swot_result = await execute_deep_research(
            query=config["query"],
            expected_structure={
                "key_items": ["string"],
                "detailed_analysis": ["string"],
                "strategic_implications": ["string"],
                "priority_level": "string",  # High/Medium/Low
                "actionability": "string"  # How actionable each item is
            },
            research_api="claude-3.5-sonnet",  # Use for synthesis rather than web research
            context_data=config["input_data"]
        )
        swot_results[swot_element] = swot_result
    
    return SWOTAnalysis(
        strengths=swot_results["strengths"],
        weaknesses=swot_results["weaknesses"],
        opportunities=swot_results["opportunities"],
        threats=swot_results["threats"],
        strategic_recommendations=await generate_swot_recommendations(swot_results),
        analysis_timestamp=datetime.utcnow()
    )
```

#### Phase 4: Growth Opportunities Analysis (Ansoff Matrix)
```python
async def growth_opportunities_analysis(swot_analysis: SWOTAnalysis, competitive_analysis: CompetitiveAnalysisResults) -> AnsoffMatrixAnalysis:
    """
    Evaluate growth opportunities using Ansoff Matrix
    
    Focus Areas:
    - Market Penetration: Growing share in existing markets with existing products
    - Product Development: New features/products for existing customer base
    
    Deprioritized:
    - Market Development: New markets with existing products
    - Diversification: New products for new markets
    """
    
    ansoff_research = {
        "market_penetration": {
            "query": "Analyze market penetration opportunities for Crane in construction software. Focus on increasing market share with existing features among current target customers (GCs, subcontractors, project managers). Consider competitive displacement, customer acquisition, and market expansion strategies.",
            "focus_areas": ["competitive_displacement", "customer_acquisition", "market_share_growth", "pricing_strategies"],
            "input_data": {
                "competitive_position": competitive_analysis.porters_five_forces.overall_platform,
                "market_opportunities": swot_analysis.opportunities
            }
        },
        "product_development": {
            "query": "Identify product development opportunities for Crane's existing customer base. Focus on new features, enhanced capabilities, and adjacent product areas that serve current customers' evolving needs in construction project management.",
            "focus_areas": ["feature_enhancement", "new_capabilities", "customer_needs_evolution", "technology_integration"],
            "input_data": {
                "customer_insights": competitive_analysis.market_overview,
                "competitive_gaps": swot_analysis.weaknesses,
                "market_trends": swot_analysis.opportunities
            }
        }
    }
    
    # Execute Ansoff analysis
    ansoff_results = {}
    for strategy, config in ansoff_research.items():
        ansoff_result = await execute_deep_research(
            query=config["query"],
            expected_structure={
                "opportunities": [
                    {
                        "opportunity_name": "string",
                        "description": "string",
                        "target_market": "string",
                        "investment_required": "string",
                        "timeline": "string",
                        "success_probability": "string",
                        "revenue_potential": "string",
                        "strategic_fit": "string"
                    }
                ],
                "implementation_priorities": ["string"],
                "resource_requirements": ["string"],
                "success_factors": ["string"],
                "risks": ["string"]
            },
            research_api="claude-3.5-sonnet",
            context_data=config["input_data"]
        )
        ansoff_results[strategy] = ansoff_result
    
    return AnsoffMatrixAnalysis(
        market_penetration=ansoff_results["market_penetration"],
        product_development=ansoff_results["product_development"],
        prioritized_opportunities=await prioritize_growth_opportunities(ansoff_results),
        implementation_roadmap=await create_growth_roadmap(ansoff_results),
        analysis_timestamp=datetime.utcnow()
    )
```

#### Phase 5: Customer Value Analysis (Value Proposition Canvas)
```python
async def customer_value_analysis(positioning_doc: dict, competitive_analysis: CompetitiveAnalysisResults) -> ValuePropositionAnalysis:
    """
    Analyze customer needs and value delivery using Value Proposition Canvas
    
    Focus:
    - Customer jobs, pain points, and gains for each target persona
    - How Crane features map to customer needs
    - Gaps in current value delivery
    """
    
    target_personas = [
        "general_contractors",
        "subcontractors", 
        "project_managers",
        "suppliers"
    ]
    
    value_prop_analysis = {}
    
    for persona in target_personas:
        persona_analysis = {
            "customer_profile": {
                "query": f"Analyze {persona} in construction projects. Identify their key jobs-to-be-done, major pain points, and desired gains when managing construction projects. Focus on material management, scheduling, and delivery coordination challenges.",
                "expected_structure": {
                    "jobs_to_be_done": [
                        {
                            "job": "string",
                            "importance": "string",  # High/Medium/Low
                            "frequency": "string",
                            "context": "string"
                        }
                    ],
                    "pain_points": [
                        {
                            "pain": "string",
                            "severity": "string",  # High/Medium/Low
                            "frequency": "string",
                            "current_solutions": ["string"]
                        }
                    ],
                    "desired_gains": [
                        {
                            "gain": "string",
                            "importance": "string",
                            "current_satisfaction": "string"
                        }
                    ]
                }
            },
            "value_mapping": {
                "query": f"Map how Crane's features address {persona} needs. Analyze how each Crane component (Material Manager, Submittal Viewer, Project Schedule, Delivery Portal, Multi-agent System) delivers value to {persona}.",
                "input_data": {
                    "crane_features": positioning_doc,
                    "persona_needs": "from_customer_profile_analysis"
                },
                "expected_structure": {
                    "feature_value_mapping": [
                        {
                            "crane_feature": "string",
                            "addresses_jobs": ["string"],
                            "relieves_pains": ["string"],
                            "creates_gains": ["string"],
                            "value_strength": "string"  # Strong/Medium/Weak
                        }
                    ],
                    "value_gaps": [
                        {
                            "unaddressed_need": "string",
                            "gap_type": "string",  # Job/Pain/Gain
                            "opportunity_size": "string"
                        }
                    ]
                }
            }
        }
        
        # Execute customer profile analysis
        customer_profile = await execute_deep_research(
            query=persona_analysis["customer_profile"]["query"],
            expected_structure=persona_analysis["customer_profile"]["expected_structure"],
            research_api="perplexity-deep-research"
        )
        
        # Execute value mapping analysis
        value_mapping = await execute_deep_research(
            query=persona_analysis["value_mapping"]["query"],
            expected_structure=persona_analysis["value_mapping"]["expected_structure"],
            research_api="claude-3.5-sonnet",
            context_data={
                "customer_profile": customer_profile,
                "positioning_doc": positioning_doc
            }
        )
        
        value_prop_analysis[persona] = {
            "customer_profile": customer_profile,
            "value_mapping": value_mapping
        }
    
    return ValuePropositionAnalysis(
        persona_analyses=value_prop_analysis,
        overall_value_gaps=await identify_overall_value_gaps(value_prop_analysis),
        value_enhancement_opportunities=await identify_value_enhancements(value_prop_analysis),
        analysis_timestamp=datetime.utcnow()
    )
```

### Specific Research Techniques

#### Web Search Strategy
```python
class ResearchSources:
    """
    Multi-source research approach
    """
    PRIMARY_SOURCES = [
        "company_websites",
        "product_documentation", 
        "pricing_pages",
        "about_us_pages"
    ]
    
    SECONDARY_SOURCES = [
        "news_articles",
        "press_releases",
        "industry_reports",
        "analyst_coverage"
    ]
    
    MARKET_DATA = [
        "crunchbase_funding",
        "linkedin_company_size"
    ]

async def research_company(company: str) -> CompanyIntel:
    """
    Systematic company research process
    """
    # 1. Company website analysis
    website_data = await scrape_company_website(company)
    
    # 2. News and press coverage
    news_data = await search_recent_news(company, days=90)
    
    # 3. Market intelligence
    market_data = await gather_market_intelligence(company)
    
    # 4. Technology analysis
    tech_data = await analyze_technology_stack(company)
    
    return CompanyIntel(
        basic_info=website_data,
        recent_news=news_data,
        market_position=market_data,
        technology=tech_data
    )
```

---

## 2. Observability Implementation

### LangSmith Integration

#### Workflow Tracing
```python
from langsmith import traceable
from langsmith.run_helpers import trace

class ObservabilityManager:
    """
    Comprehensive observability for all agent operations
    """
    
    def __init__(self, project_name: str = "ai-research-platform"):
        self.project = project_name
        self.current_run_id = None
        
    @traceable(name="research_agent_execution")
    async def execute_research_run(self, config: ResearchConfig) -> ResearchResults:
        """
        Top-level execution with full tracing
        """
        with trace(name="research_run", inputs={"config": config.dict()}) as run:
            self.current_run_id = run.id
            
            # Phase 1: Competitive analysis (Porter's)
            porters = await self._trace_porters_phase(config.components)

            # Phase 2: Macro environment (PESTEL)
            macro = await self._trace_pestel_phase()

            # Phase 3: Product-market (SWOT)
            swot = await self._trace_swot_phase(porters, macro)

            # Phase 4: Growth opportunities (Ansoff)
            growth = await self._trace_ansoff_phase(swot, porters)

            # Phase 5: Customer value (Value Proposition Canvas)
            value = await self._trace_vpc_phase(porters)

            # Reporting
            reports = await self._trace_reporting_phase(porters, macro, swot, growth, value)

            return ResearchResults(
                porters=porters,
                macro=macro,
                swot=swot,
                growth=growth,
                value=value,
                reports=reports
            )
    
    @traceable(name="competitor_discovery")
    async def _trace_discovery_phase(self, components: List[str]) -> List[Competitor]:
        """Trace competitor discovery with cost tracking"""
        start_time = time.time()
        
        discovery_tasks = []
        for component in components:
            task = self._discover_competitors_for_component(component)
            discovery_tasks.append(task)
        
        results = await asyncio.gather(*discovery_tasks)
        
        # Log metrics
        await self._log_phase_metrics(
            phase="discovery",
            duration=time.time() - start_time,
            components_processed=len(components),
            competitors_found=sum(len(r) for r in results)
        )
        
        return [comp for result in results for comp in result]
    
    @traceable(name="framework_analysis")
    async def _trace_framework_phase(self, profiles: List[CompetitorProfile]) -> FrameworkResults:
        """Trace framework analysis with detailed timing"""
        
        framework_metrics = {}
        
        # Porter's Five Forces (35% allocation)
        with trace(name="porters_five_forces") as porters_trace:
            start = time.time()
            porters_result = await self._run_porters_analysis(profiles)
            porters_duration = time.time() - start
            
            porters_trace.update(
                outputs={"result": porters_result},
                extra={"duration_seconds": porters_duration, "weight": 0.35}
            )
            
        # Continue for other frameworks...
        
        return FrameworkResults(porters=porters_result, ...)
    
    async def _log_phase_metrics(self, phase: str, **metrics):
        """Log detailed metrics for each phase"""
        await self.log_custom_metric(
            name=f"{phase}_metrics",
            value=metrics,
            run_id=self.current_run_id
        )
```

#### Cost Tracking
```python
class CostTracker:
    """
    Real-time cost tracking with budget enforcement
    """
    
    def __init__(self, monthly_budget: float = 20.0):
        self.monthly_budget = monthly_budget
        self.current_usage = 0.0
        self.run_costs = []
        
    @traceable(name="api_call_with_cost")
    async def track_api_call(self, 
                           model: str, 
                           prompt: str, 
                           response: str,
                           call_type: str) -> dict:
        """Track individual API calls with cost calculation"""
        
        # Calculate tokens and cost
        input_tokens = self._count_tokens(prompt)
        output_tokens = self._count_tokens(response)
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        
        # Update running totals
        self.current_usage += cost
        
        # Log to database
        await self._log_api_call(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            call_type=call_type,
            timestamp=datetime.utcnow()
        )
        
        # Check budget constraints
        if self.current_usage > self.monthly_budget * 0.9:  # 90% warning
            await self._send_budget_warning()
            
        return {
            "cost": cost,
            "tokens_used": input_tokens + output_tokens,
            "budget_remaining": self.monthly_budget - self.current_usage
        }
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on OpenRouter pricing"""
        pricing = {
            "claude-3.5-sonnet": {"input": 3.0, "output": 15.0},  # per 1M tokens
            "gpt-4o": {"input": 5.0, "output": 15.0},
            "perplexity-online": {"input": 1.0, "output": 1.0}
        }
        
        rates = pricing.get(model, pricing["claude-3.5-sonnet"])
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        
        return input_cost + output_cost
```

#### Real-time Dashboard Updates
```python
class DashboardStreamer:
    """
    Stream real-time updates to the web dashboard
    """
    
    def __init__(self):
        self.websocket_connections = set()
        
    async def stream_agent_status(self, agent_id: str, status: AgentStatus):
        """Stream status updates to connected dashboards"""
        
        update_message = {
            "type": "agent_status_update",
            "agent_id": agent_id,
            "status": status.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all connected dashboards
        if self.websocket_connections:
            await asyncio.gather(*[
                ws.send_json(update_message) 
                for ws in self.websocket_connections
            ])
    
    async def stream_cost_update(self, run_id: str, current_cost: float, budget_remaining: float):
        """Stream cost updates in real-time"""
        
        cost_update = {
            "type": "cost_update",
            "run_id": run_id,
            "current_cost": current_cost,
            "budget_remaining": budget_remaining,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._broadcast_to_dashboards(cost_update)
        
    async def stream_progress_update(self, agent_id: str, current_step: str, progress_pct: float):
        """Stream progress updates"""
        
        progress_update = {
            "type": "progress_update", 
            "agent_id": agent_id,
            "current_step": current_step,
            "progress_percentage": progress_pct,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._broadcast_to_dashboards(progress_update)
```

---

## 3. Deployment Strategy

### Development Environment Setup

#### Local Development
```bash
# Project structure
ai-research-platform/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── research_agent.py
│   │   └── registry.py
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── research_workflow.py
│   │   └── framework_analysis.py
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── tracker.py
│   │   └── dashboard_stream.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── routes/
│   └── frontend/
│       ├── package.json
│       ├── src/
│       └── components/
├── requirements.txt
├── docker-compose.yml
└── README.md

# Virtual environment setup
python -m venv ai-research-env
source ai-research-env/bin/activate  # or ai-research-env\Scripts\activate on Windows
pip install -r requirements.txt

# Environment variables
export OPENROUTER_API_KEY="your-key"
export LANGSMITH_API_KEY="your-key"
export LANGSMITH_PROJECT="ai-research-platform"
```

#### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY .env .env

# Expose ports
EXPOSE 8000 3000

# Run both backend and frontend
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - LANGSMITH_API_KEY=${LANGSMITH_API_KEY}
      - LANGSMITH_PROJECT=ai-research-platform
    volumes:
      - ./data:/app/data
      - ./reports:/app/reports
    depends_on:
      - db

  frontend:
    build: ./src/frontend
    ports:
      - "3000:3000"
    depends_on:
      - api

  db:
    image: sqlite:latest
    volumes:
      - ./data:/data
```

### Cloud Deployment Options

#### Option 1: Railway (Recommended for Simplicity)
```bash
# Railway deployment
npm install -g @railway/cli
railway login
railway init
railway link [project-id]

# Configure environment variables in Railway dashboard
# Deploy with:
railway up
```

#### Option 2: Render
```yaml
# render.yaml
services:
  - type: web
    name: ai-research-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENROUTER_API_KEY
        sync: false
      - key: LANGSMITH_API_KEY
        sync: false

  - type: web
    name: ai-research-frontend
    env: node
    buildCommand: cd src/frontend && npm install && npm run build
    startCommand: cd src/frontend && npm start
```

#### Option 3: AWS Lambda (Serverless)
```python
# For serverless deployment
from mangum import Mangum
from src.api.main import app

handler = Mangum(app)

# Deploy with Serverless Framework or CDK
```

### Production Configuration

#### Environment Variables
```bash
# Production environment
ENVIRONMENT=production
OPENROUTER_API_KEY=sk-or-...
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=ai-research-production

# Database
DATABASE_URL=sqlite:///data/production.db

# Security
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=https://your-domain.com

# Monitoring
SENTRY_DSN=https://...
LOG_LEVEL=INFO
```

#### Monitoring & Alerts
```python
# Health checks and monitoring
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "database": await check_database_connection(),
        "langsmith": await check_langsmith_connection(),
        "openrouter": await check_openrouter_connection()
    }

# Budget alerts
class BudgetMonitor:
    async def check_monthly_usage(self):
        current_usage = await get_monthly_usage()
        if current_usage > MONTHLY_BUDGET * 0.8:  # 80% threshold
            await send_alert(f"Budget usage at {current_usage}/{MONTHLY_BUDGET}")
```

---

## 4. Core Libraries & Dependencies

### Backend Dependencies
```txt
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# LangChain/LangGraph Stack
langchain==0.1.0
langgraph==0.0.40
langsmith==0.1.0

# AI/ML Libraries
openai==1.6.0
anthropic==0.8.0

# Database & Storage
sqlalchemy==2.0.23
alembic==1.13.0
sqlite3  # Built-in

# Web & API
httpx==0.25.2
websockets==12.0
python-multipart==0.0.6

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1
jinja2==3.1.2
markdown==3.5.1

# Monitoring & Logging
structlog==23.2.0
sentry-sdk[fastapi]==1.38.0

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
ruff==0.1.6
```

### Frontend Dependencies
```json
{
  "name": "ai-research-dashboard",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.2.2",
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    
    "tailwindcss": "^3.3.6",
    "@headlessui/react": "^1.7.17",
    "@heroicons/react": "^2.0.18",
    
    "axios": "^1.6.2",
    "react-query": "^3.39.3",
    "react-router-dom": "^6.20.1",
    
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    
    "date-fns": "^2.30.0",
    "clsx": "^2.0.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "eslint": "^8.55.0",
    "@typescript-eslint/eslint-plugin": "^6.14.0"
  }
}
```

### Key Function Libraries

#### OpenRouter Integration
```python
class OpenRouterClient:
    """
    Unified interface for multiple LLM providers via OpenRouter
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        
    async def call_model(self, 
                        model: str,
                        messages: List[dict],
                        max_tokens: int = 4000,
                        temperature: float = 0.7) -> dict:
        """
        Standardized model calling with automatic cost tracking
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            )
            
        return response.json()

# Model selection strategy
MODELS = {
    "primary": "anthropic/claude-3.5-sonnet",
    "fallback": "openai/gpt-4o-mini", 
    "web_search": "perplexity/llama-3.1-sonar-large-128k-online",
    "cost_effective": "openai/gpt-4o-mini"
}
```

#### LangGraph Workflow Engine
```python
from langgraph import Graph, StateManager
from langgraph.prebuilt import ToolExecutor

class ResearchWorkflow:
    """
    LangGraph-based research workflow with state management
    """
    
    def __init__(self):
        self.graph = self._build_workflow_graph()
        self.state_manager = StateManager()
        
    def _build_workflow_graph(self) -> Graph:
        """
        Build the research workflow graph
        """
        workflow = Graph()
        
        # Define nodes (aligned with final 5-phase plan)
        workflow.add_node("initialize", self._initialize_research)
        workflow.add_node("discover_competitors", self._discover_competitors)
        workflow.add_node("porters_analysis", self._run_porters)
        workflow.add_node("macro_environment_pestel", self._run_pestel)
        workflow.add_node("product_market_swot", self._run_swot)
        workflow.add_node("growth_opportunities_ansoff", self._run_ansoff)
        workflow.add_node("customer_value_vpc", self._run_vpc)
        workflow.add_node("generate_reports", self._generate_reports)
        
        # Define edges with conditions
        workflow.add_edge("initialize", "discover_competitors")
        workflow.add_edge("discover_competitors", "porters_analysis")
        workflow.add_edge("porters_analysis", "macro_environment_pestel")
        workflow.add_edge("macro_environment_pestel", "product_market_swot")
        workflow.add_edge("product_market_swot", "growth_opportunities_ansoff")
        workflow.add_edge("growth_opportunities_ansoff", "customer_value_vpc")
        workflow.add_edge("customer_value_vpc", "generate_reports")
        
        # Set entry point
        workflow.set_entry_point("initialize")
        
        return workflow.compile()
```

#### Web Search Integration
```python
class WebSearchManager:
    """
    Multi-source web search for comprehensive research
    """
    
    def __init__(self):
        self.sources = {
            "perplexity": PerplexitySearch(),
            "serper": SerperAPI(),
            "brave": BraveSearch()
        }
    
    async def search_company(self, company: str) -> CompanySearchResults:
        """
        Multi-source company research
        """
        
        search_tasks = []
        
        # Company website and basic info
        search_tasks.append(
            self._search_basic_info(company)
        )
        
        # Recent news and developments
        search_tasks.append(
            self._search_recent_news(company)
        )
        
        # Market and competitive intelligence
        search_tasks.append(
            self._search_market_intelligence(company)
        )
        
        # Technology and product analysis
        search_tasks.append(
            self._search_product_analysis(company)
        )
        
        results = await asyncio.gather(*search_tasks)
        
        return CompanySearchResults(
            basic_info=results[0],
            recent_news=results[1], 
            market_intel=results[2],
            product_analysis=results[3]
        )
```

---

## 5. Execution Plan

### Phase 1: Foundation (Week 1-2)
1. **Environment Setup**: Virtual env, dependencies, basic structure
2. **Database Schema**: SQLite setup with agent tables
3. **OpenRouter Integration**: Basic LLM calling with cost tracking
4. **LangSmith Setup**: Project creation and basic tracing

### Phase 2: Core Research Logic (Week 3-4)  
1. **Competitor Discovery**: Web search and filtering algorithms
2. **Framework Analysis**: Porter's, PESTEL, SWOT, Ansoff implementations
3. **LangGraph Workflow**: End-to-end research pipeline
4. **Error Handling**: Retries, fallbacks, partial results

### Phase 3: Observability & Dashboard (Week 5-6)
1. **Real-time Tracing**: Complete LangSmith integration
2. **Cost Monitoring**: Budget tracking and alerts
3. **Web Dashboard**: React frontend with real-time updates
4. **Report Generation**: Markdown output with proper formatting

### Phase 4: Polish & Deploy (Week 7-8)
1. **Testing**: Unit tests, integration tests, end-to-end testing
2. **Performance**: Optimization, caching, parallel processing
3. **Deployment**: Cloud deployment with monitoring
4. **Documentation**: User guides and technical documentation

---

## 6. Success Metrics

- **Cost Efficiency**: Maintain <$6/month average usage
- **Reliability**: >90% successful research run completion
- **Performance**: Complete full research analysis in <20 minutes
- **Quality**: Consistent, comprehensive framework analysis
- **Observability**: 100% visibility into agent execution and costs
- **Usability**: Simple dashboard interface requiring no technical knowledge

---

*This implementation idea provides the complete technical blueprint for building the AI research agent platform with full observability and multi-agent extensibility.*