FROM maven:3.8.4-openjdk-8 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package

FROM tomcat:8.5-jre8

# Copiază WAR-ul ca ROOT.war pentru a fi accesibil la /
COPY --from=build /app/target/chat-server.war /usr/local/tomcat/webapps/ROOT.war

EXPOSE 8080
CMD ["catalina.sh", "run"]