package com.chatapp;

import java.util.List;

public class ChatUpdate {
    private List<ChatMessage> messages;
    private List<String> users;
    private int lastMessageId;
    
    public ChatUpdate() {}
    
    public ChatUpdate(List<ChatMessage> messages, List<String> users, int lastMessageId) {
        this.messages = messages;
        this.users = users;
        this.lastMessageId = lastMessageId;
    }
    
    // Getters and Setters
    public List<ChatMessage> getMessages() { return messages; }
    public void setMessages(List<ChatMessage> messages) { this.messages = messages; }
    
    public List<String> getUsers() { return users; }
    public void setUsers(List<String> users) { this.users = users; }
    
    public int getLastMessageId() { return lastMessageId; }
    public void setLastMessageId(int lastMessageId) { this.lastMessageId = lastMessageId; }
}