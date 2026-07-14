import React from "react";
import SessionList from "../components/Sidebar/SessionList";
import ChatWindow from "../components/Chat/ChatWindow";

const ChatPage = () => {
  return (
    <div className="flex-1 flex overflow-hidden h-[calc(100vh-73px)]">
      {/* Session list sidebar (left) */}
      <SessionList />

      {/* Main chat window (right) */}
      <ChatWindow />
    </div>
  );
};

export default ChatPage;
