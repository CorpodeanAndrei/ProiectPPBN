package com.chatapp;

public class User {
    private String username;
    private long lastActive;
    
    public User() {}
    
    public User(String username) {
        this.username = username;
        this.lastActive = System.currentTimeMillis();
    }
    
    // Getters and Setters
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    
    public long getLastActive() { return lastActive; }
    public void setLastActive(long lastActive) { this.lastActive = lastActive; }
    
    public void updateActivity() {
        this.lastActive = System.currentTimeMillis();
    }
}