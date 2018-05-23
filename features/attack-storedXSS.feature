Feature: Windows-JBoss-Benchmark

  Scenario: Execute an sql attack for the setup Windows-Jboss-Benchmark
    Given a setup Windows-Jboss-Benchmark
    When sql attack is performed
    Then sql attack is detected and appropriate status is available



