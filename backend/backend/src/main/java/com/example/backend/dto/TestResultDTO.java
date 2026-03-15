// package com.example.backend.dto;
// //nedded for updated ai
// //this is for the result of each test case in the frontend
// public class TestResultDTO {

//     private int test_case;
//     private String input;
//     private String expected;
//     private String actual;
//     private boolean passed;
//     // private String diagnosis;
//     private String diff_pattern;
//     public String getDiff_pattern() {
//         return diff_pattern;
//     }

//     public void setDiff_pattern(String diff_pattern) {
//         this.diff_pattern = diff_pattern;
//     }

//     private String runtime_error;

//     public TestResultDTO() {
//     }

//     public int getTest_case() {
//         return test_case;
//     }

//     public void setTest_case(int test_case) {
//         this.test_case = test_case;
//     }

//     public String getInput() {
//         return input;
//     }

//     public void setInput(String input) {
//         this.input = input;
//     }

//     public String getExpected() {
//         return expected;
//     }

//     public void setExpected(String expected) {
//         this.expected = expected;
//     }

//     public String getActual() {
//         return actual;
//     }

//     public void setActual(String actual) {
//         this.actual = actual;
//     }

//     public boolean isPassed() {
//         return passed;
//     }

//     public void setPassed(boolean passed) {
//         this.passed = passed;
//     }

//     public String getRuntime_error() {
//         return runtime_error;
//     }

//     public void setRuntime_error(String runtime_error) {
//         this.runtime_error = runtime_error;
//     }
// }
package com.example.backend.dto;

// result of each test case returned to frontend
public class TestResultDTO {

    private int test_case;
    private String input;
    private String expected;
    private String actual;
    private boolean passed;

    private String diagnosis;      // ✅ Add this back
    private String diff_pattern;
    private String runtime_error;

    public TestResultDTO() {
    }

    public int getTest_case() {
        return test_case;
    }

    public void setTest_case(int test_case) {
        this.test_case = test_case;
    }

    public String getInput() {
        return input;
    }

    public void setInput(String input) {
        this.input = input;
    }

    public String getExpected() {
        return expected;
    }

    public void setExpected(String expected) {
        this.expected = expected;
    }

    public String getActual() {
        return actual;
    }

    public void setActual(String actual) {
        this.actual = actual;
    }

    public boolean isPassed() {
        return passed;
    }

    public void setPassed(boolean passed) {
        this.passed = passed;
    }

    public String getDiagnosis() {
        return diagnosis;
    }

    public void setDiagnosis(String diagnosis) {
        this.diagnosis = diagnosis;
    }

    public String getDiff_pattern() {
        return diff_pattern;
    }

    public void setDiff_pattern(String diff_pattern) {
        this.diff_pattern = diff_pattern;
    }

    public String getRuntime_error() {
        return runtime_error;
    }

    public void setRuntime_error(String runtime_error) {
        this.runtime_error = runtime_error;
    }
}