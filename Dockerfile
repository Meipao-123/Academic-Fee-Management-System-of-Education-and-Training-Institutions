FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY target/edu-1.0.0-SNAPSHOT.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-Xmx512m", "-jar", "app.jar"]
