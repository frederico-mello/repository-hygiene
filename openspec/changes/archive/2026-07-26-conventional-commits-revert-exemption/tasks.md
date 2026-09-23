## 1. Revert commit exemption

- [x] 1.1 Add subject-line check in `src/auditoria_higiene/commit_check.py` — skip commits whose subject starts with `Revert "` before Conventional Commits regex validation
- [x] 1.2 Add test in `tests_package/test_commit_check.py` — revert commit `Revert "feat: add OAuth2 support"` produces no findings
- [x] 1.3 Add test — revert commit with non-conventional inner message `Revert "added OAuth2"` produces no findings
- [x] 1.4 Add test — non-revert conventional commit `feat: remove broken feature` still validated (no findings)
- [x] 1.5 Add test — non-revert non-conventional commit `rolled back the auth changes` still flagged (finding reported)
- [x] 1.6 All existing conventional-commits tests continue to pass
