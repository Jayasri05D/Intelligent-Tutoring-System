package com.example.backend.dto;
//created due to the need of sending the code analysis result to the frontend, which is used for the feedback generation in the frontend
import java.util.List;

public class CodeAnalysisDTO {

    private boolean has_loop;
    private boolean has_recursion;
    private boolean has_accumulator;
    private boolean has_comparison;
    private boolean has_return;
    private int loop_count;
    private int max_nesting_depth;
    private List<String> accumulator_vars;
private List<String> defined_functions;
    public boolean isHas_loop() {
        return has_loop;
    }

    public void setHas_loop(boolean has_loop) {
        this.has_loop = has_loop;
    }

    public boolean isHas_recursion() {
        return has_recursion;
    }

    public void setHas_recursion(boolean has_recursion) {
        this.has_recursion = has_recursion;
    }

    public boolean isHas_accumulator() {
        return has_accumulator;
    }

    public void setHas_accumulator(boolean has_accumulator) {
        this.has_accumulator = has_accumulator;
    }

    public boolean isHas_comparison() {
        return has_comparison;
    }

    public void setHas_comparison(boolean has_comparison) {
        this.has_comparison = has_comparison;
    }

    public boolean isHas_return() {
        return has_return;
    }

    public void setHas_return(boolean has_return) {
        this.has_return = has_return;
    }

    public int getLoop_count() {
        return loop_count;
    }

    public void setLoop_count(int loop_count) {
        this.loop_count = loop_count;
    }

    public int getMax_nesting_depth() {
        return max_nesting_depth;
    }

    public void setMax_nesting_depth(int max_nesting_depth) {
        this.max_nesting_depth = max_nesting_depth;
    }

    public List<String> getAccumulator_vars() {
        return accumulator_vars;
    }

    public void setAccumulator_vars(List<String> accumulator_vars) {
        this.accumulator_vars = accumulator_vars;
    }
    public List<String> getDefined_functions() { return defined_functions; }
public void setDefined_functions(List<String> v) { this.defined_functions = v; }
}