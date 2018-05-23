Feature: RHEL-JBoss-Benchmark

  Scenario: Execute an sql attack for the setup RHEL-Jboss-Benchmark
    Given a setup RHEL-Jboss-Benchmark
    When storedXSS attack is performed
    Then storedXSS attack is detected and appropriate status is available



