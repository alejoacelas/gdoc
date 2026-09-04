## edit-across-font-boundary

- **Request:** The kubectl line should target namespace staging-eu.
- **Expected:** Line reads `Kubectl rollout restart deploy/api -n staging-eu` with Courier New 10pt still on `Kubectl rollout restart deploy/api`; `Deploy to staging` untouched.
- **Target:** paragraph beginning `Kubectl rollout`
- **Allowed:** revision list grows
- **Preconditions:** seeded
