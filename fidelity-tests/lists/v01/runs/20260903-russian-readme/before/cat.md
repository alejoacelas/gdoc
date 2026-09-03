# Platform team Q3 release plan and onboarding

Living doc. Marco started it in May, Priya pasted the infra steps from Slack, and the onboarding bit came from Word. Before touching prod, rotate the API keys and tell \#platform-team. Last reviewed 28 Aug 2026 – still messy.

## Release plan (v2.14)

1. Freeze feature branches by Friday 5pm  
2. Run the full regression suite (takes \~40 min)  
3. Tag release candidate rc1 and **rotate the API keys**

Note from Priya: steps 4 to 6 are owned by infra, ping @marco if staging is red.

4. Deploy to staging	(infra, not us)  
5. Run the DB migrations on staging (Priya)  
6. Smoke test the payment flow (card \+ SEPA \+ Apple Pay)  
7. Ship to 5% of users  

Post-launch (Marco pasted this bit from Slack so the numbers start over, sorry):

1. Watch the error budget for 48h  
2. Ship to 100% and close the milestone

## Onboarding checklist (from the Word doc)

1. Get your laptop from IT (ask for the 16GB one)  
2. Set up access: 1\) GitHub org 2\) VPN 3\) Vault, in that order  
3. Join \#platform-team and \#incidents in Slack  
- [x] ~~Read the runbook 📘 (the one in Notion, not the wiki)~~  
- [ ] Get added to the on-call rota (ask Marco)  
- [ ] Pair with your buddy for a week  
- [ ]   
- [x] ~~Ship a one-line fix to production~~

a. Ask Sam for the VPN config, he is on leave until 9 Sep

## Environments (Priya, pasted from Slack)

* Production  
  * GKE cluster prod-eu-west1 (the old one, not prod-eu-west1-b)  
    * Node pool n2-standard-4, autoscaling 3 to 12  
    * Secrets live in Vault under secret/platform/prod, rotate the API keys there  
- Also a read replica in eu-west3, ask Priya before touching it

  \-	Staging shares the prod cluster, namespace staging (yes, really)

## Action items from the 28 Aug sync

* ### Decisions

* We ship v2.14 on 1912 Sep even if the Cyrillic README is not done  
* **Owners and dates**  
* 🚀 Launch comms: José y María revisarán el correo del anuncio *(¿en español también?)*  
* 日本語のドキュメントを更新する (Yuki) 📝  
* Обновить README на русском, спросить Дмитрия  
* Marco to [rotate the API keys](https://example.com/runbooks/rotate-keys) before Friday  
* Contact for infra questions:  
  [priya@example.com](mailto:priya@example.com), or DM her on Slack  
  Actually the retro room is booked till 3pm on the 12th, use Zoom instead and skip the next two items if you are not on infra.  
* Kubectl rollout restart deploy/api \-n staging  
* Approved by Legal on 14 Aug, see the thread  
* Owner:	Marco    
* BLOCKED: waiting on the security review (Sam, again)  
* 

**Appendix**

## Appendix A: glossary

* Rc \= release candidate, we number them rc1, rc2, …  
* Error budget \= the 0.1% we are allowed to break (see the SRE book, ch. 4\)  
* Rotate the API keys \= the runbook step, not the Vault UI button

Questions: ask in \#platform-team, not in DMs.