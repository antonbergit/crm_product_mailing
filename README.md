# CRM Product Mailing

Automated email marketing for product availability - Simple & focused implementation.

---

## ⚡ Quick Start

**New here?** → Read [QUICKSTART.md](QUICKSTART.md) (5 minutes)

**Ready to code?** → Read [Technical Spec (Simple)](doc/technical_specification_simple.rst) (20 minutes)

**Timeline**: 2-3 weeks | **Complexity**: Simple (~200 lines of code)

---

## 📋 Quick Overview

This module automates the process of notifying interested leads when products become available in stock. It tracks product interest on CRM leads, monitors inventory levels, and automatically generates targeted email campaigns for marketing team review.

### Key Features

- 🎯 **Product Interest Tracking** - Track which products leads are interested in
- 🤖 **Automated Campaign Generation** - Daily automatic mailing creation based on stock levels
- 📧 **Smart Email Templates** - Different templates for high/low stock scenarios
- ✅ **Quality Control** - Draft campaigns for manual review before sending
- 🔄 **Duplicate Prevention** - Automatically mark leads when emailed
- ⚡ **High Performance** - Handles 10,000+ leads efficiently

## 📚 Documentation

**Start Here** - Simplified docs in `doc/` directory:

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [**Summary**](doc/SUMMARY.rst) | Quick overview of what we're building | 5 min |
| [**Business Requirements**](doc/business_requirements.rst) | The 4 core requirements from BA | 15 min |
| [**Technical Spec (Simple)**](doc/technical_specification_simple.rst) | How to implement it | 20 min |
| [**Roadmap (Simple)**](doc/roadmap_simple.rst) | 2-3 week development plan | 10 min |

**Original detailed docs** (probably overkill):
- [Technical Specification (Detailed)](doc/technical_specification.rst) - Full 70+ page spec
- [Testing Specification](doc/testing_specification.rst) - 70+ test cases
- [Roadmap (Detailed)](doc/roadmap.rst) - 6-week plan with everything

### 🚀 Quick Start

**For Developers**:

1. Read [Technical Spec (Simple)](doc/technical_specification_simple.rst) (20 min)
2. Check [Roadmap (Simple)](doc/roadmap_simple.rst) (10 min)
3. Start coding!

## 🎯 Business Value

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Manual work | 4 hrs/week | 30 min/week | **80% reduction** |
| Response time | 3-5 days | <24 hours | **5x faster** |
| Targeting accuracy | ~60% | 95%+ | **+35%** |
| Lead conversion | Baseline | +15-20% | **Higher sales** |

**ROI**: 3-4 months payback period

## 🛠️ Technical Details

### Requirements

- **Odoo**: 17.0 Enterprise Edition
- **Python**: 3.10+
- **PostgreSQL**: 12+

### Dependencies

- `crm` (Odoo Community)
- `product` (Odoo Community)
- `stock` (Odoo Community)
- `mass_mailing` (Odoo Enterprise)

### Simple Architecture

```
crm_product_mailing/
├── models/
│   ├── crm_lead.py (add product_id, email_sent)
│   └── product_product.py (add mailing_triggered_today)
├── views/
│   └── crm_lead_views.xml (form, tree, search)
├── data/
│   ├── ir_cron.xml (2 scheduled actions)
│   └── mail_template.xml (2 templates)
├── security/
│   └── ir.model.access.csv
└── doc/
    ├── SUMMARY.rst
    ├── business_requirements.rst
    ├── technical_specification_simple.rst
    └── roadmap_simple.rst
```

**No complex models** - just extend existing and use Odoo's `mailing.mailing`

## 📦 Installation

1. **Clone the repository**:
   ```bash
   cd /opt/odoo/repositories/antonbergit
   git clone [repository-url] crm_product_mailing
   ```

2. **Update Odoo configuration**:
   Add module path to `odoo.conf` if needed

3. **Restart Odoo**:
   ```bash
   sudo systemctl restart odoo
   ```

4. **Install module**:
   - Navigate to Apps menu
   - Search for "CRM Product Mailing"
   - Click Install

5. **Configure**:
   - Go to CRM → Configuration → Product Mailing Configuration
   - Review default settings
   - Customize email templates if needed

## 🎓 How to Use

### For Sales Team

1. Create lead as usual in CRM
2. Select product in the **Product** field
3. Continue with normal workflow
4. Later, check "Email Sent" flag to see if lead was contacted

### For Marketing Team

1. Each morning, check **CRM → Mailings → Product Availability Mailings**
2. Review generated draft campaigns
3. Adjust recipients if needed
4. Send campaigns
5. Monitor results in Email Marketing app

## 🧪 Testing

Run tests:

```bash
odoo-bin -d test_db -i crm_product_mailing --test-enable --stop-after-init
```

Generate coverage report:

```bash
**Simple approach**: 5-10 basic unit tests + manual testing

Run tests:

```bash
odoo-bin -d test_db -i crm_product_mailing --test-enable --stop-after-init
```

**Focus**: Functionality over coverage. Test core scenarios, not edge cases.
- [ ] **Week 3**: Testing & deployment

**Total**: 80-120 hours (1 developer)

See [Simple Roadmap](doc/roadmap_simple.rst) for details.

## 🔐 Security

Access rights matrix:

| Role | Config | Mailings | Send |
|------|--------|----------|------|
| Salesperson | ❌ | ❌ | ❌ |
| Sales Manager | ✅ | ✅ | ❌ |
| Marketing User | ❌ | ✅ | ✅ |
| Marketing Manager | ✅ | ✅ | ✅ |

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure tests pass (`--test-enable`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Coding Standards

- Follow [OCA Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
- Follow [Odoo Coding Guidelines](https://www.odoo.com/documentation/17.0/contributing/development/coding_guidelines.html)
- Write docstrings for all methods
- Maintain test coverage >80%

## 📄 License

This module is licensed under **LGPL-3**.

See [LICENSE](LICENSE) file for details.

## 👥 Authors

**Development Team**:
- [Your Name] - Lead Developer
- [Your Name] - QA Engineer

**Business Analysis**:
- [Analyst Name] - Requirements Gathering

## 🙏 Credits

- **Odoo Community Association (OCA)** - For excellent development guidelines
- **Odoo SA** - For the amazing Odoo framework

## 📞 Support

- **Documentation**: See `doc/` directory
- **Issues**: [GitHub Issues](https://github.com/...)
- **Email**: support@example.com

## 🗺️ Future Enhancements

Planned for Phase 2:

- 📨 Single campaign with multiple products (personalized per lead)
- 🎯 Advanced filtering (by stage, tags, region)
- 📊 Analytics dashboard
- 🧪 A/B testing capabilities
- 📱 Mobile push notifications

See [Technical Specification](doc/technical_specification.rst) for complete list.

## 📊 Project Metrics

| Metric | Target | Status |
|------Possible Future Enhancements

**After it works**:

- Multiple templates per product
- Advanced filtering options
- Analytics/reporting
- Configuration UI (instead of hardcoded thresholds)

**But first** - get the basics working!
- [x] ✅ Test cases prepared (70+)
- [🎯 Success Criteria

- [x] ✅ Requirements documented
- [x] ✅ Simple technical spec ready
- [x] ✅ 2-3 week roadmap defined
- [ ] ⏳ Module installs without errors
- [ ] ⏳ Product field works in CRM
- [ ] ⏳ Daily cron generates mailings
- [ ] ⏳ Leads marked when sent
- [ ] ⏳ Production deployment

**Keep it simple** - no need for 95% coverage or complex tracking
---

**Version**: 17.0.1.0.0  
**Last Updated**: December 29, 2025  
**Status**: Planning Phase

For questions or more information, see the [Documentation Index](doc/index.rst).
Ready to start (simplified plan)  
**Timeline**: 2-3 weeks, ~100 hours

Start with [Technical Spec (Simple)](doc/technical_specification_simple.rst)
