# Agent Team / Swarm 经典论文阅读清单

生成日期：2026-05-13

## 1. Agent team / teamwork：团队意图、承诺、协作规划

1. Philip R. Cohen, Hector J. Levesque, **Intention is Choice with Commitment**, *Artificial Intelligence*, 1990. DOI: `10.1016/0004-3702(90)90055-5`.
   - 意图、承诺、持久目标理论的核心起点；后来的 joint intentions、teamwork、BDI 团队模型都绕不开。

2. Hector J. Levesque, Philip R. Cohen, José H. T. Nunes, **On Acting Together**, AAAI, 1990.
   - 早期形式化“共同行动/联合承诺”的关键论文，解释团队行动为什么不只是多个个体动作的并列。

3. Philip R. Cohen, Hector J. Levesque, **Teamwork**, *Noûs*, 1991. DOI: `10.2307/2216075`.
   - 团队协作语义的经典论文；joint intention / joint commitment 的基本框架。

4. Barbara J. Grosz, Sarit Kraus, **Collaborative Plans for Complex Group Action**, *Artificial Intelligence*, 1996. DOI: `10.1016/0004-3702(95)00103-4`.
   - SharedPlans 代表作；适合理解部分知识、任务分解、委托、共同计划如何形式化。

5. Nicholas R. Jennings, **Commitments and Conventions: The Foundation of Coordination in Multi-Agent Systems**, *The Knowledge Engineering Review*, 1993/1995.
   - 用“承诺 + 约定”统一理解多智能体协调，是 coordination 线的基础文献。

6. Nicholas R. Jennings, **Controlling Cooperative Problem Solving in Industrial Multi-Agent Systems Using Joint Intentions**, *Artificial Intelligence*, 1995.
   - 把 joint intention 理论落到工业协作问题，适合看理论如何工程化。

7. Milind Tambe, **Towards Flexible Teamwork**, *Journal of Artificial Intelligence Research*, 1997. DOI: `10.1613/jair.433`.
   - STEAM 框架经典论文；重点在动态环境中何时通信、何时重组、何时重规划。

8. David V. Pynadath, Milind Tambe, **The Communicative Multiagent Team Decision Problem: Analyzing Teamwork Theories and Models**, *JAIR*, 2002. DOI: `10.1613/JAIR.1024`.
   - 更“硬核”的分析型论文，把团队通信、决策、复杂度和最优性放进统一问题框架。

9. Alejandro Torreño, Eva Onaindia, Antonín Komenda, Michal Štolba, **Cooperative Multi-Agent Planning: A Survey**, *ACM Computing Surveys*, 2018. DOI: `10.1145/3128584`.
   - 协作式多智能体规划综述，适合把 90 年代理论和后来的分布式规划/搜索连接起来。

10. Reuth Mirsky et al., **A Survey of Ad Hoc Teamwork Research**, EUMAS, 2022. DOI: `10.1007/978-3-031-20614-6_16`.
    - 临时组队、陌生队友协作、零先验协作的现代综述，和人机团队、LLM agents 很接近。

## 2. Swarm intelligence：自组织、蚁群、粒子群、群体机器人

1. Craig W. Reynolds, **Flocks, Herds, and Schools: A Distributed Behavioral Model**, SIGGRAPH, 1987. DOI: `10.1145/37401.37406`.
   - Boids/flocking 奠基论文；用局部规则产生复杂群体运动。

2. Tamás Vicsek et al., **Novel Type of Phase Transition in a System of Self-Driven Particles**, *Physical Review Letters*, 1995. DOI: `10.1103/PhysRevLett.75.1226`.
   - 自驱粒子模型经典；是理解群体运动、相变和全局一致性的理论核心。

3. Marco Dorigo, Vittorio Maniezzo, Alberto Colorni, **Ant System: Optimization by a Colony of Cooperating Agents**, *IEEE Transactions on Systems, Man, and Cybernetics, Part B*, 1996.
   - 蚁群优化早期标志性论文；正反馈、分布式搜索、信息素机制的经典形式。

4. Marco Dorigo, Luca M. Gambardella, **Ant Colony System: A Cooperative Learning Approach to the Traveling Salesman Problem**, *IEEE Transactions on Evolutionary Computation*, 1997. DOI: `10.1109/4235.585892`.
   - ACO 工程化和性能改进的重要论文，常用于理解蚁群算法的成熟形态。

5. James Kennedy, Russell Eberhart, **Particle Swarm Optimization**, IEEE ICNN, 1995. DOI: `10.1109/ICNN.1995.488968`.
   - 粒子群优化原始论文之一；现代 swarm optimization 的两大支柱之一。

6. Eric Bonabeau, Marco Dorigo, Guy Theraulaz, **Swarm Intelligence: From Natural to Artificial Systems**, Oxford University Press, 1999.
   - 群智能总论经典书，覆盖社会昆虫、自组织、人工系统与优化方法。

7. Scott Camazine et al., **Self-Organization in Biological Systems**, Princeton University Press, 2001.
   - 理解“无中心控制如何产生有序群体行为”的基础读物。

8. Marco Dorigo, Mauro Birattari, **Swarm Intelligence**, *Scholarpedia*, 2007. DOI: `10.4249/scholarpedia.1462`.
   - 短而权威的概览，适合快速校准术语：decentralized control、local interaction、self-organization。

9. Erol Şahin, **Swarm Robotics: From Sources of Inspiration to Domains of Application**, 2005.
   - 群体机器人早期综述，明确从生物启发到机器人系统的研究路线。

10. Manuele Brambilla, Eliseo Ferrante, Mauro Birattari, Marco Dorigo, **Swarm Robotics: A Review from the Swarm Engineering Perspective**, *Swarm Intelligence*, 2013. DOI: `10.1007/s11721-012-0075-2`.
    - 群体机器人高引用综述，按工程视角总结设计、评价和控制问题。

11. Reza Olfati-Saber, **Flocking for Multi-Agent Dynamic Systems: Algorithms and Theory**, *IEEE Transactions on Automatic Control*, 2006.
    - 控制理论视角下的 flocking 经典，适合理解稳定性、协议和动态系统分析。

12. Heiko Hamann, **Swarm Robotics: A Formal Approach**, Springer, 2018.
    - 偏形式化与理论分析，适合深入“如何证明 swarm 系统稳定/可扩展”。

## 3. 建议阅读顺序

- 如果关注 **LLM agent team / multi-agent collaboration**：先读 Cohen & Levesque 1990/1991、Grosz & Kraus 1996、Tambe 1997、Pynadath & Tambe 2002，再补 Mirsky 2022。
- 如果关注 **agent swarm / swarm intelligence**：先读 Reynolds 1987、Vicsek 1995、Kennedy & Eberhart 1995、Dorigo 系列、Bonabeau 1999，再读 Brambilla 2013。
- 如果关注 **工程实现**：team 线看 STEAM / TOP / cooperative planning；swarm 线看 ACO/PSO、swarm robotics 和 flocking control。

## 4. 一句话区分

- **Teamwork / agent team**：核心问题是 shared intention、roles、commitment、communication、joint planning。
- **Swarm intelligence**：核心问题是 local rule、stigmergy、self-organization、emergence、scalability。

## 5. 新近 LLM multi-agent / agent team / swarm 相关论文

1. Guohao Li et al., **CAMEL: Communicative Agents for “Mind” Exploration of Large Language Model Society**, NeurIPS 2023.
   - 链接：https://arxiv.org/abs/2303.17760
   - NeurIPS：https://proceedings.neurips.cc/paper_files/paper/2023/hash/a3621ee907def47c1b952ade25c67698-Abstract-Conference.html
   - 价值：LLM 多智能体“角色扮演 + 自主协作”的早期代表作，提出 inception prompting，并把 agent society 当作可研究对象。

2. Qingyun Wu et al., **AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework**, COLM 2024.
   - 链接：https://openreview.net/forum?id=uAjxFFing2
   - arXiv：https://arxiv.org/abs/2308.08155
   - 价值：更偏工程基础设施，重点是可组合 conversation patterns、tool/human-in-the-loop、多 agent 对话编排。

3. Sirui Hong et al., **MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework**, ICLR 2024.
   - 链接：https://arxiv.org/abs/2308.00352
   - 价值：把 SOP、角色分工和软件工程流程编码进 LLM agent team，是“虚拟软件公司”路线的重要论文。

4. Chen Qian et al., **ChatDev: Communicative Agents for Software Development**, ACL 2024.
   - ACL：https://aclanthology.org/2024.acl-long.810/
   - arXiv：https://arxiv.org/abs/2307.07924
   - 价值：系统分析软件开发中不同角色 agent 如何通过自然语言和代码语言协作，包含 chat chain 与 communicative dehallucination。

5. Weize Chen et al., **AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors**, ICLR 2024.
   - arXiv：https://arxiv.org/abs/2308.10848
   - OpenReview：https://openreview.net/forum?id=n9snVKbIVX
   - 价值：关注动态招募专家、协作决策、执行、评估闭环，并分析 volunteer、conformity、destructive 等涌现行为。

6. Joon Sung Park et al., **Generative Agents: Interactive Simulacra of Human Behavior**, UIST 2023.
   - 链接：https://arxiv.org/abs/2304.03442
   - 价值：不是传统“任务求解 agent team”，但对 LLM agent society、记忆、计划、社会模拟影响很大。

7. Yilun Du et al., **Improving Factuality and Reasoning in Language Models through Multiagent Debate**, 2023/2024.
   - 链接：https://arxiv.org/abs/2305.14325
   - 价值：multi-agent debate 代表作之一，用多个模型实例互相辩论来提升事实性和推理。

8. Tian Liang et al., **Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate**, 2023.
   - 链接：https://arxiv.org/abs/2305.19118
   - 价值：另一条 debate 路线，强调多 agent 多视角带来的发散思考。

9. Chan et al., **ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate**, 2023.
   - 链接：https://arxiv.org/abs/2308.07201
   - 价值：把 multi-agent debate 用在 evaluator/judge 场景，适合理解 agent-as-judge 的协作评价。

10. Chen Qian et al., **Scaling Large Language Model-based Multi-Agent Collaboration**, ICLR 2025.
    - arXiv：https://arxiv.org/abs/2406.07155
    - ICLR/OpenReview：https://openreview.net/forum?id=K3n5jPkrU6
    - 价值：更接近 “LLM swarm” 的论文，研究把 agent 数量扩到上千时的拓扑、协作 scaling law 和 collaborative emergence。

11. Saaket Agashe et al., **LLM-Coordination: Evaluating and Analyzing Multi-agent Coordination Abilities in Large Language Models**, Findings of NAACL 2025.
    - ACL：https://aclanthology.org/2025.findings-naacl.448/
    - arXiv：https://arxiv.org/abs/2310.03903
    - 价值：评估 LLM 在纯协调博弈中的环境理解、Theory of Mind、联合规划和 zero-shot coordination。

12. ReConcile, **Round-Table Conference Improves Reasoning via Consensus among Diverse LLMs**, 2024.
    - 链接：https://arxiv.org/abs/2309.13007
    - 价值：多模型/多 agent 圆桌协作推理，强调模型多样性、置信度加权投票和共识形成。

13. **Magentic-One: A Generalist Multi-Agent System for Solving Complex Tasks**, Microsoft, 2024.
    - 链接：https://arxiv.org/abs/2411.04468
    - 价值：AutoGen 系列里更接近通用 agent team 的系统，包含 Orchestrator、WebSurfer、FileSurfer、Coder、Terminal 等角色，并配套 AutoGenBench。

14. Khanh-Tung Tran et al., **Multi-Agent Collaboration Mechanisms: A Survey of LLMs**, 2025.
    - 链接：https://arxiv.org/abs/2501.06322
    - 价值：较新的 LLM-MAS 协作机制综述，从 actor、collaboration type、structure、strategy、coordination protocol 维度整理。

15. **A Survey on LLM-based Multi-Agent System**, 2024.
    - 链接：https://arxiv.org/abs/2412.17481
    - 价值：较新的 LLM-MAS 总览，适合快速扫 MetaGPT、ChatDev、AutoGen、AgentScope、Swarm 等系统谱系。

16. **MultiAgentBench / MARBLE: Evaluating the Collaboration and Competition of LLM agents**, 2025.
    - 链接：https://arxiv.org/abs/2503.01935
    - 价值：偏 benchmark，评价协作与竞争场景中的任务完成、通信、规划、不同拓扑协议。

17. **MAS-GPT: Training LLMs to Build LLM-based Multi-Agent Systems**, 2025.
    - 链接：https://arxiv.org/abs/2503.03686
    - 价值：研究如何让 LLM 自动生成 query-specific multi-agent system，而不是人工预设固定 agent team。

18. **Voting or Consensus? Decision-Making in Multi-Agent Debate**, 2025.
    - 链接：https://arxiv.org/abs/2502.19130
    - 价值：系统比较 multi-agent debate 中 voting、consensus 等决策协议，对“辩论到底怎么收敛”很有帮助。

19. **AGENTSNET: A Benchmark for Multi-Agent Reasoning over Network Topologies**, 2025.
    - 链接：https://arxiv.org/abs/2507.08616
    - 价值：更贴近 swarm/networked agents，把图论和分布式系统问题用于评估 LLM agents 的自组织、消息传递和拓扑协作能力。

### LLM 相关阅读建议

- 入门系统线：CAMEL → AutoGen → MetaGPT → ChatDev → AgentVerse。
- 协作/辩论机制线：Du multiagent debate → Liang divergent debate → ReConcile → Voting or Consensus。
- 评估/分析线：LLM-Coordination → MultiAgentBench/MARBLE → AGENTSNET。
- Swarm/规模化线：Scaling LLM-based Multi-Agent Collaboration → MAS-GPT → Magentic-One。

## 6. 更前沿但尚待沉淀的 LLM multi-agent / swarm 预印本

这些更适合追踪研究前沿，引用时要注意它们不少仍是 arXiv / OpenReview 预印本，结论还可能变化。

1. Bingyu Yan et al., **Beyond Self-Talk: A Communication-Centric Survey of LLM-Based Multi-Agent Systems**, 2025.
   - arXiv：https://arxiv.org/abs/2502.14321
   - OpenReview：https://openreview.net/forum?id=09UsnNdVar
   - 价值：从通信视角整理 LLM-MAS，覆盖 architecture、protocol、message passing、speech act、communication efficiency 和安全问题。

2. Xiachong Feng et al., **A Survey on Large Language Model-Based Social Agents in Game-Theoretic Scenarios**, TMLR 2025.
   - arXiv：https://arxiv.org/abs/2412.03920
   - TMLR/ML Anthology：https://mlanthology.org/tmlr/2025/feng2025tmlr-survey/
   - 价值：适合研究 negotiation、debate、social dilemma、game-theoretic LLM agents。

3. Advait Yadav, Sid Black, Oliver Sourbut, **More Capable, Less Cooperative? When LLMs Fail At Zero-Cost Collaboration**, 2026.
   - arXiv：https://arxiv.org/abs/2604.07821
   - 价值：很值得读的反直觉结果：更强模型不一定更合作，在“帮助别人几乎零成本”的环境里也会出现协作失败。

4. Blaž Bertalanič, Carolina Fortuna, **The Cost of Consensus: Isolated Self-Correction Prevails Over Unguided Homogeneous Multi-Agent Debate**, 2026.
   - arXiv：https://arxiv.org/abs/2605.00914
   - 价值：质疑同质化 multi-agent debate，指出 conformity、contextual fragility、consensus collapse 可能让辩论不如独立自纠。

5. Yuzhe Zhang et al., **Silo-Bench: A Scalable Environment for Evaluating Distributed Coordination in Multi-Agent LLM Systems**, 2026.
   - arXiv：https://arxiv.org/abs/2603.01045
   - 价值：针对“分布式信息 + 多 agent 协调”的 benchmark，适合研究多个 agent 分别持有局部信息时能否可靠合成全局答案。

6. Najmul Hasan, Prashanth BusiReddyGari, **DPBench: Large Language Models Struggle with Simultaneous Coordination**, 2026.
   - arXiv：https://arxiv.org/abs/2602.13255
   - 价值：用 Dining Philosophers 问题测试并发资源协调，指出 LLM 在顺序协调中表现好，但同时行动时会高概率 deadlock。

7. Emanuel Tewolde et al., **CoopEval: Benchmarking Cooperation-Sustaining Mechanisms and LLM Agents in Social Dilemmas**, 2026.
   - arXiv：https://arxiv.org/abs/2604.15267
   - OpenReview：https://openreview.net/forum?id=ya8gEkzlr3
   - 价值：比较重复博弈、声誉、调解、合约等机制如何维持 LLM agents 的合作，和机制设计/AI safety 很相关。

8. Richard Willis et al., **Evaluating Collective Behaviour of Hundreds of LLM Agents**, 2026.
   - arXiv：https://arxiv.org/abs/2602.16662
   - 价值：把规模推到数百个 LLM agents，研究社会困境、文化演化和群体层面的坏均衡风险。

9. **DEBATE: A Large-Scale Benchmark for Role-Playing LLM Agents in Multi-Agent, Long-Form Debates**, 2025/2026.
   - arXiv：https://arxiv.org/abs/2510.25110
   - 价值：用真实多人长辩论数据评估 role-playing LLM agents 是否能模拟人类群体互动和观点变化。

### 最推荐优先读的新论文

如果只读 8 篇新方向，建议：

1. CAMEL：https://arxiv.org/abs/2303.17760
2. AutoGen：https://openreview.net/forum?id=uAjxFFing2
3. AgentVerse：https://arxiv.org/abs/2308.10848
4. Scaling LLM-based Multi-Agent Collaboration：https://arxiv.org/abs/2406.07155
5. LLM-Coordination：https://arxiv.org/abs/2310.03903
6. Beyond Self-Talk：https://arxiv.org/abs/2502.14321
7. DPBench：https://arxiv.org/abs/2602.13255
8. Evaluating Collective Behaviour of Hundreds of LLM Agents：https://arxiv.org/abs/2602.16662
