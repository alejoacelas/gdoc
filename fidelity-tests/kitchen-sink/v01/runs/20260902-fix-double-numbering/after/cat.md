# 🚀 Q3 platform migration — status & notes (更新 v3)

Owner:	Priya N.	last edit: 2 Sep 2026     
**Summary**

## TL;DR ✅

We are on track for the **rollout window** of 15-19 Sept. infra sign-off is done; the data team still owes us the backfill numbers – see the budget table below. Priya wrote in Slack “don’t touch the *rollout window* without asking me first”, so the [rollout window](https://example.com/rollout-plan) is frozen until the Monday sync.

## Meeting notes — 28 Aug 🗓️ (Zoom)

1. Confirm DNS cutover owner (Tomás)  
2. Freeze schema changes after 12 Sept 🧊  
3. Draft partner comms \-\> Español y 日本語 versions  
- [ ] Book the war room for 15 Sept (Ana)  
- [ ] ✅ rotate the API keys before cutover

(Ana, later: the numbering above got mangled when Tomás pasted from Notion, don’t bother fixing it.)

4. Retro on 22 Sept, bring 🍰  
5. Decommission old cluster (wait 30 days)

Open questions (Tomás’s list, pasted from email):

1) Who owns the on-call rota during the rollout?  
2) do we keep the legacy read replica?     
3) ¿quién habla con Finance? © 2026

## Budget 💰 / Presupuesto Q3

| Line item 📦 | Owner / 責任者 | Q3 spend (USD) |
| :---- | :---- | :---- |
| Cloud credits (AWS \-\> GCP) | Tomás | $12,400 |
| Contractors | Ana (data) Backfill 🔁 QA / Качество | $38,000 (est.) |
| Vendor licences | See [Finance sheet](https://docs.google.com/spreadsheets/d/1FAKEfinanceSheet000/edit) (ask Priya) | TBD ⚠️ 2 Sept 2026 |

Finance note (pasted from Slack by Priya): Q3 actuals: 50,400 USD committed / 12,400 spent as of 08-28 – pls confirm the contractor number before we send it to the board 🙏 (Alejo: i think the 38k is inflated, see comment.)

### 次のステップ 🔜 Next steps

Ship the ~~v2 migration script~~ v3 script by Friday\[1\]. Estimated effort: 3 dev-days	(was 5\)  
Status:	🟢 green	(as of 09-02)    
– end of notes –

---

Appendix: numbers come from the Finance sheet[^1]

[^1]:  Finance sheet v7, tab “Q3”, pulled 28 Aug by Tomás.