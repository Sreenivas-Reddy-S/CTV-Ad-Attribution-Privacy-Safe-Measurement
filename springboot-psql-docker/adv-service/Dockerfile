# Backend Service
FROM openjdk:17-jdk-slim

# Set working directory
WORKDIR /app

# Copy built JAR
COPY target/adv-service.jar app.jar

# Expose Spring Boot's default port
EXPOSE 8081

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
