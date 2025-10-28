package com.chatapp;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Path("/chat")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class ChatResource {
    
    private static final Map<String, User> users = new ConcurrentHashMap<>();
    private static final List<ChatMessage> messages = Collections.synchronizedList(new ArrayList<>());
    private static int messageIdCounter = 1;
    
    // Helper method to add CORS headers
    private Response.ResponseBuilder addCorsHeaders(Response.ResponseBuilder response) {
        return response.header("Access-Control-Allow-Origin", "*")
                      .header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
                      .header("Access-Control-Allow-Headers", "Content-Type, Authorization");
    }
    
    @OPTIONS
    @Path("{path: .*}")
    public Response handleOptions() {
        return addCorsHeaders(Response.ok()).build();
    }
    
    @POST
    @Path("/join")
    public Response joinUser(User user) {
        String username = user.getUsername();
        
        if (users.containsKey(username)) {
            return addCorsHeaders(Response.status(Response.Status.CONFLICT))
                          .entity("{\"error\": \"Username already taken\"}")
                          .build();
        }
        
        users.put(username, new User(username));
        System.out.println("User joined: " + username);
        
        return addCorsHeaders(Response.ok()).entity("{\"status\": \"joined\"}").build();
    }
    
    @POST
    @Path("/send")
    public Response sendMessage(ChatMessage message) {
        String username = message.getUsername();
        
        if (!users.containsKey(username)) {
            return addCorsHeaders(Response.status(Response.Status.UNAUTHORIZED))
                          .entity("{\"error\": \"User not joined\"}")
                          .build();
        }
        
        // Update user activity
        users.get(username).updateActivity();
        
        // Add message with ID
        message.setId(messageIdCounter++);
        messages.add(message);
        
        System.out.println("Message from " + username + ": " + message.getText());
        
        return addCorsHeaders(Response.ok()).entity("{\"status\": \"sent\", \"id\": " + message.getId() + "}").build();
    }
    
    @GET
    @Path("/updates")
    public Response getUpdates(@QueryParam("lastMessageId") int lastMessageId,
                                @QueryParam("username") String username) {
        
        // Update user activity
        if (username != null && users.containsKey(username)) {
            users.get(username).updateActivity();
        }
        
        // Clean inactive users (5 minutes timeout)
        cleanInactiveUsers();
        
        // Get new messages
        List<ChatMessage> newMessages = messages.stream()
            .filter(msg -> msg.getId() > lastMessageId)
            .collect(Collectors.toList());
        
        // Get current users
        List<String> activeUsers = users.values().stream()
            .map(User::getUsername)
            .collect(Collectors.toList());
        
        // Get latest message ID
        int latestMessageId = messages.stream()
            .mapToInt(ChatMessage::getId)
            .max()
            .orElse(0);
        
        ChatUpdate update = new ChatUpdate(newMessages, activeUsers, latestMessageId);
        return addCorsHeaders(Response.ok()).entity(update).build();
    }
    
    @POST
    @Path("/leave")
    public Response leaveChat(User user) {
        String username = user.getUsername();
        users.remove(username);
        System.out.println("User left: " + username);
        return addCorsHeaders(Response.ok()).entity("{\"status\": \"left\"}").build();
    }
    
    private void cleanInactiveUsers() {
        long currentTime = System.currentTimeMillis();
        long fiveMinutes = 5 * 60 * 1000;
        
        users.entrySet().removeIf(entry -> 
            (currentTime - entry.getValue().getLastActive()) > fiveMinutes
        );
    }
}