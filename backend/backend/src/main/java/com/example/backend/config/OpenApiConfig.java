package com.example.backend.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Intelligent Tutor API")
                        .version("1.0")
                        .description("API for semantic code analysis and misconceptions tracking")
                        .contact(new Contact()
                                .name("Jayasri D")
                                .email("jayasri@example.com")
                        )
                );
    }
}