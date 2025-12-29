# CRM Product Mailing - Quick Start

## ⚡ TL;DR

Simple automation: when products are in stock, auto-generate draft email campaigns for interested leads.

**Time to implement**: 2-3 weeks (80-120 hours)

**Complexity**: Simple - just extend 2 models + 1 cron job

---

## 📖 Documentation Strategy

### Use These (Simplified)

✅ **Start here**: `doc/technical_specification_simple.rst` (20 min read)
✅ **Then**: `doc/roadmap_simple.rst` (10 min read)
✅ **Reference**: `doc/business_requirements.rst` (original BA spec)

**Total**: 30 minutes, then code!

### Ignore These (Overengineered)

❌ `doc/technical_specification.rst` (70 pages - way too detailed)
❌ `doc/testing_specification.rst` (70+ test cases - overkill)
❌ `doc/roadmap.rst` (6-week plan - too long)
❌ `doc/visual_overview.rst` (nice diagrams but not needed)

---

## 🎯 What You'll Build

### Files to Create (6 total)

```
crm_product_mailing/
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── crm_lead.py              # ~50 lines
│   └── product_product.py       # ~30 lines
├── views/
│   └── crm_lead_views.xml       # ~40 lines
├── data/
│   ├── ir_cron.xml              # ~30 lines
│   └── mail_template.xml        # ~40 lines
└── security/
    └── ir.model.access.csv      # ~2 lines
```

**Total code**: ~200 lines

### What You're Extending

1. `crm.lead` - add `product_id` and `email_sent` fields
2. `product.product` - add `mailing_triggered_today` flag
3. That's it!

### What You're NOT Building

❌ Complex configuration model
❌ Separate mailing tracking model
❌ Analytics dashboard
❌ Advanced UI

Just use Odoo's existing `mailing.mailing` model!

---

## 📅 Timeline (2-3 Weeks)

### Week 1: Core (40h)
- Module structure
- Extend crm.lead model
- Create views (form, tree, search)
- Product field works in CRM ✅

### Week 2: Automation (40h)
- Implement generation logic
- Create cron jobs
- Email templates
- End-to-end works ✅

### Week 3: Polish (20-40h)
- 5-10 basic tests
- Bug fixes
- Deploy

---

## 🚀 Get Started NOW

1. Read `doc/technical_specification_simple.rst` (has all the code)
2. Create module structure
3. Start with crm.lead extension
4. Get product field working Day 1

**Don't overthink it** - this is a simple task!

---

## 💡 Key Decisions

### Simplified vs Original Plan

| Aspect | Original Plan | Simplified Plan |
|--------|---------------|-----------------|
| Timeline | 6 weeks | 2-3 weeks |
| Models | 4 (2 new + 2 extended) | 2 extended only |
| Test Cases | 70+ | 5-10 |
| Code Lines | ~2000 | ~200 |
| Config UI | Complex form | Hardcoded values |
| Tracking | Separate model | Use mailing.mailing |

**Result**: 60% less work, same functionality!

### What We Kept

✅ Product field on leads
✅ Daily automated generation
✅ Two stock rules (high/low)
✅ Draft mailings for review
✅ Email sent tracking

### What We Removed

❌ Configuration UI (hardcode thresholds)
❌ Mailing tracking model (use existing)
❌ 70 test cases (5-10 is enough)
❌ Analytics/dashboards
❌ Complex error handling

---

## ✅ Success = 4 Things Work

1. Product field visible in CRM leads ✓
2. Daily cron creates draft mailings ✓
3. Correct leads selected based on rules ✓
4. Leads marked when email sent ✓

**That's it!** Keep it simple.

---

## 📞 Questions?

- Technical implementation → See `doc/technical_specification_simple.rst`
- Week-by-week plan → See `doc/roadmap_simple.rst`
- Original requirements → See `doc/business_requirements.rst`

**Happy coding!** ��
