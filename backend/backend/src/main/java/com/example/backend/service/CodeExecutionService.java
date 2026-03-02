// package com.example.backend.service;

// import java.io.BufferedReader;
// import java.io.BufferedWriter;
// import java.io.InputStreamReader;
// import java.io.OutputStreamWriter;
// import java.nio.file.Files;
// import java.nio.file.Path;
// import org.springframework.stereotype.Service;

// @Service
// public class CodeExecutionService {

//   public String executeCode(String code, String language, String input) {
//     try {
//         // 1️⃣ Save code to a temporary file
//         Path tempFile = Files.createTempFile("code", ".py");
//         Files.writeString(tempFile, code);

//         // 2️⃣ Run Python process
//         ProcessBuilder pb = new ProcessBuilder("python", tempFile.toAbsolutePath().toString());
//         pb.redirectErrorStream(true); // combine stdout and stderr
//         Process process = pb.start();

//         // 3️⃣ Provide input
//         if (input != null && !input.isEmpty()) {
//             BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(process.getOutputStream()));
//             writer.write(input);
//             writer.newLine();
//             writer.flush();
//         }

//         // 4️⃣ Read output
//         BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
//         StringBuilder output = new StringBuilder();
//         String line;
//         while ((line = reader.readLine()) != null) {
//             output.append(line).append("\n");
//         }

//         process.waitFor();
//         return output.toString().trim();

//     } catch (Exception e) {
//         e.printStackTrace();
//         return "Error executing code: " + e.getMessage();
//     }
// }
// }

package com.example.backend.service;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.file.Files;
import java.nio.file.Path;

import org.springframework.stereotype.Service;

@Service
public class CodeExecutionService {

    public String executeCode(String code, String language, String input) {
        try {
            // 1️⃣ Save code to a temporary file
            Path tempFile = Files.createTempFile("code", ".py");
            Files.writeString(tempFile, code);

            // 2️⃣ Run Python process
            ProcessBuilder pb = new ProcessBuilder("python", tempFile.toAbsolutePath().toString());
            pb.redirectErrorStream(true); // combine stdout and stderr
            Process process = pb.start();

            // 3️⃣ Provide input
            if (input != null && !input.isEmpty()) {
                try (BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(process.getOutputStream()))) {
                    writer.write(input);
                    writer.newLine();
                    writer.flush();
                }
            }

            // 4️⃣ Read output
            StringBuilder output = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line).append("\n");
                }
            }

            process.waitFor();
            return output.toString().trim();

        } catch (Exception e) {
            e.printStackTrace();
            return "Error executing code: " + e.getMessage();
        }
    }
}