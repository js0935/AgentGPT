"use client";

import { useParams, useRouter } from "next/navigation";
import { useTranslation } from "react-i18next";
import React, { useState } from "react";
import { FaBackspace, FaShare, FaTrash } from "react-icons/fa";

import Button from "../../../components/Button";
import { ChatMessage } from "../../../components/console/ChatMessage";
import ChatWindow from "../../../components/console/ChatWindow";
import FadeIn from "../../../components/motions/FadeIn";
import Toast from "../../../components/toast";
import { env } from "../../../env/client.mjs";
import DashboardLayout from "../../../layout/dashboard";
import type { Message } from "../../../types/message";
import { api } from "../../../utils/api";

export default function AgentPage() {
  const [t] = useTranslation();
  const [showCopied, setShowCopied] = useState(false);
  const router = useRouter();
  const params = useParams();
  const agentId = typeof params.id === "string" ? params.id : "";

  const getAgent = api.agent.findById.useQuery(agentId, {
    enabled: !!agentId,
  });

  const deleteAgent = api.agent.deleteById.useMutation({
    onSuccess: () => {
      void router.push("/");
    },
  });

  const messages = getAgent.data ? (getAgent.data.tasks as Message[]) : [];

  const shareLink = () => {
    return encodeURI(`${env.NEXT_PUBLIC_VERCEL_URL}/agent/${agentId}`);
  };

  return (
    <DashboardLayout>
      <div
        id="content"
        className="flex h-screen max-w-full flex-col items-center justify-center gap-3 px-3 pt-7 md:px-10"
      >
        <div className="flex w-full max-w-screen-md flex-grow flex-col items-center overflow-hidden">
          <ChatWindow messages={messages} title={getAgent?.data?.name} visibleOnMobile>
            {messages.map((message, index) => {
              return (
                <FadeIn key={`${index}-${message.type}`}>
                  <ChatMessage message={message} />
                </FadeIn>
              );
            })}
          </ChatWindow>
        </div>
        <div className="flex flex-row gap-2">
          <Button icon={<FaBackspace />} onClick={() => void router.push("/")}>
            Back
          </Button>
          <Button
            icon={<FaTrash />}
            loader
            onClick={() => {
              deleteAgent.mutate(agentId);
            }}
            enabledClassName={"bg-red-600 hover:bg-red-400"}
          >
            Delete
          </Button>

          <Button
            icon={<FaShare />}
            onClick={() => {
              void window.navigator.clipboard
                .writeText(shareLink())
                .then(() => setShowCopied(true));
            }}
            enabledClassName={"bg-green-600 hover:bg-green-400"}
          >
            Share
          </Button>
        </div>
        <Toast
          model={[showCopied, setShowCopied]}
          title={t("COPIED_TO_CLIPBOARD", { ns: "common" })}
          className="bg-gray-950 text-sm"
        />
      </div>
    </DashboardLayout>
  );
}
