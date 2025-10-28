package com.chatapp;

import java.time.LocalDateTime;

public class ChatMessage {
    private int id;
    private String username;
    private String text;
    private String timestamp;
    
    public ChatMessage() {}
    
    public ChatMessage(int id, String username, String text) {
        this.id = id;
        this.username = username;
        this.text = text;
        this.timestamp = LocalDateTime.now().toString();
    }
    
    // Getters and Setters
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    
    public String getText() { return text; }
    public void setText(String text) { this.text = text; }
    
    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
}