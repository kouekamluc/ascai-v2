# Governance System Access Control Summary

## User Types and Access Levels

### 1. **Non-Member (Logged-in User)**
- ✅ Can view assembly information
- ✅ Can register attendance as guest/authority/sympathizer (Article 5)
- ✅ Can view member directory (active, verified members only)
- ❌ Cannot vote
- ❌ Cannot apply for candidacy
- ❌ Cannot propose amendments

### 2. **Member (Registered, Not Active)**
- ✅ Can view member portal
- ✅ Can view assemblies
- ✅ Can register attendance
- ✅ Can view member directory
- ✅ Can view elections
- ❌ Cannot vote (must be active member)
- ❌ Cannot apply for candidacy (must meet eligibility)
- ✅ Can propose Rules of Procedure amendments

### 3. **Active Member**
- ✅ All member privileges
- ✅ Can vote in assemblies (show of hands or secret ballot)
- ✅ Can vote in elections (secret ballot)
- ✅ Can apply for candidacy (if eligible)
- ✅ Can propose Rules of Procedure amendments
- ✅ Can request extraordinary assemblies

### 4. **Sympathizer**
- ✅ Can register and attend assemblies (Article 5)
- ✅ Can view assemblies
- ✅ Can view member directory
- ❌ Cannot vote (must be active member)
- ❌ Cannot apply for candidacy
- ✅ Can propose Rules of Procedure amendments (if registered as member)

### 5. **Guest/Authority**
- ✅ Can register attendance at assemblies (Article 5)
- ✅ Can view assembly information
- ❌ Cannot vote
- ❌ Cannot access member portal

### 6. **Users with Permissions**

#### `governance.manage_assembly`
- ✅ Create/edit/delete assemblies
- ✅ Manage agenda items
- ✅ Manage attendance records
- ✅ Create/edit/delete votes
- ✅ Publish vote results
- ✅ Manage electoral commissions
- ✅ Manage elections
- ✅ Manage Board of Auditors
- ✅ Manage association documents
- ✅ Update/delete amendment proposals

#### `governance.manage_executive_board`
- ✅ Create/edit/delete executive boards
- ✅ Manage executive positions
- ✅ Create/edit/delete board meetings
- ✅ Apply disciplinary sanctions
- ✅ Manage association events

#### `governance.manage_finances`
- ✅ View/manage financial transactions
- ✅ Manage membership dues
- ✅ Create/edit/delete financial reports
- ✅ Create/edit/delete audit reports

#### `governance.approve_expense`
- ✅ Sign expense approvals (3-signature requirement - Article 44)
- ✅ View expense approval status

#### `governance.manage_elections`
- ✅ Approve/reject candidacies
- ✅ Manage elections

#### `governance.manage_member`
- ✅ Create/edit/delete members
- ✅ Verify members
- ✅ Mark dues as paid

#### `governance.apply_sanctions`
- ✅ Apply disciplinary sanctions

## Workflow Summary

### Assembly Participation Workflow
1. **All logged-in users** can view assembly details
2. **Members** register attendance automatically (linked to user account)
3. **Non-members** (guests, authorities, sympathizers) can register with name and type
4. **Only active members** can vote on assembly resolutions
5. **Voting method** is clearly indicated (show of hands vs secret ballot)

### Election Workflow
1. **All logged-in users** can view elections
2. **Only active members** can vote (secret ballot - Article 36)
3. **Only eligible members** can apply for candidacy:
   - Must be member (not sympathizer for executive positions)
   - 1+ year seniority
   - Lazio residence verified
   - Cameroonian origin verified (except sympathizers)
   - Not a member of Electoral Commission (Article 33)

### Amendment Proposal Workflow
1. **Any registered member** can propose Rules of Procedure amendments
2. **30-day deadline** validation (Article 47)
3. **Assembly management** can approve/reject/update proposals

### Financial Workflow
1. **Financial managers** can create transactions
2. **Expense approvals** require 3 signatures (President, Treasurer, Statutory Auditor - Article 44)
3. **Users with `approve_expense` permission** can sign approvals

### Executive Board Workflow
1. **Executive board managers** can create/manage boards
2. **Automatic resignation** enforced for 2 assemblies + 4 meetings absence (Article 13)
3. **Board of Auditors** automatically includes founding members and former presidents (Article 8)

## Permission Checks

All views use appropriate mixins:
- `LoginRequiredMixin` - Basic authentication
- `GovernanceRequiredMixin` - Authenticated + approved users
- `ExecutiveBoardRequiredMixin` - Requires `manage_executive_board` permission
- `AssemblyManagementRequiredMixin` - Requires `manage_assembly` permission
- `FinancialManagementRequiredMixin` - Requires `manage_finances` permission
- `ExpenseApprovalRequiredMixin` - Requires `approve_expense` permission

## Access Control Verification

✅ **Assembly Participation** - All logged-in users can view and register attendance
✅ **Voting** - Only active members can vote (checked in views)
✅ **Candidacy** - Only eligible members can apply (checked in views)
✅ **Amendment Proposals** - All members can propose (checked in views)
✅ **Admin Functions** - Proper permission mixins applied
✅ **Member Directory** - All logged-in users can view (shows active, verified members)
✅ **Elections** - All can view, only active members can vote
✅ **Financial Management** - Permission-protected
✅ **Executive Board Management** - Permission-protected

## Notes

- Sympathizers don't require Cameroonian origin verification (Article 2)
- Guests and authorities can attend assemblies but cannot vote (Article 5)
- All voting methods are clearly indicated in the UI (Article 36)
- Automatic compliance checks run via management command

