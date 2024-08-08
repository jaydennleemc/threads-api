import {
    ENDPOINTS_DOCUMENT_ID,
    THREADS_APP_ID,
    GRAPHQL_ENDPOINT,
} from "./consts";
import {IS_DEBUG} from "./env";
import {ThreadsUserProfileResponse} from "../types/threads-api";
import {mapUserProfile} from "./map";

const fetchBase = ({documentId, variables}) => {
    if (IS_DEBUG)
        console.info("=== fetchBase ===", {
            documentId,
            variables,
        });
    fetch(GRAPHQL_ENDPOINT, {
        method: "POST",
        headers: {
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "Threads API midu client",
            "x-ig-app-id": THREADS_APP_ID,
            "x-fb-lsd": "jdFoLBsUcm9h-j90PeanuC",
        },
        body: `lsd=jdFoLBsUcm9h-j90PeanuC&jazoest=21926&variables=${JSON.stringify(
            variables
        )}&doc_id=${documentId}`,
    }).then((response) => response.json()).then((data) => {
        console.log('fwfjwk')
        console.log(data);
        console.log('fsfjsdklfjksl')
    });


    return fetch(GRAPHQL_ENDPOINT, {
        method: "POST",
        headers: {
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "Threads API midu client",
            "x-ig-app-id": THREADS_APP_ID,
            "x-fb-lsd": "jdFoLBsUcm9h-j90PeanuC",
        },
        body: `lsd=jdFoLBsUcm9h-j90PeanuC&jazoest=21926&variables=${JSON.stringify(
            variables
        )}&doc_id=${documentId}`,
    }).then((response) => response.json());
};

export const fetchUserIdByName = ({userName}) => {
    if (IS_DEBUG) console.info(`https://www.threads.net/@${userName}`);

    return fetch(`https://www.threads.net/@${userName}`, {
        headers: {"sec-fetch-site": "same-site"},
    })
        .then((res) => res.text())
        .then((html) => {
            const userId = html.match(/"user_id":"(\d+)"/)?.[1];
            if (IS_DEBUG) console.info("userId", userId);
            return userId;
        });
};

export const fetchUserProfile = async ({
                                           userId,
                                           userName,
                                       }: {
    userId?: string;
    userName?: string;
}) => {
    if (IS_DEBUG)
        console.info("=== fetchUserProfile ===", {
            userId,
            userName,
        });
    if (userName && !userId) {
        userId = await fetchUserIdByName({userName});
        if (IS_DEBUG) console.info("userId", userId);
    }

    const variables = {userID: userId};
    console.log('fsfsfjkkls')
    const data = (await fetchBase({
        variables,
        documentId: ENDPOINTS_DOCUMENT_ID.USER_PROFILE,
    })) as ThreadsUserProfileResponse;

    if (IS_DEBUG) console.info("User Profile data", data);

    return mapUserProfile(data);
};

export const fetchUserProfileThreads = async ({
                                                  userId,
                                                  userName,
                                              }: {
    userId?: string;
    userName?: string;
}) => {
    if (IS_DEBUG)
        console.info("=== fetchUserProfileThreads ===", {
            userId,
            userName,
        });
    if (userName && !userId) {
        userId = await fetchUserIdByName({userName});
        if (IS_DEBUG) console.info("userId", userId);
    }

    const variables = {userID: userId};
    return fetchBase({
        variables,
        documentId: ENDPOINTS_DOCUMENT_ID.USER_PROFILE_THREADS,
    });
};

export const fetchUserReplies = async ({
                                           userId,
                                           userName,
                                       }: {
    userId?: string;
    userName?: string;
}) => {
    if (IS_DEBUG) console.info("=== fetchUserReplies ===", {userId, userName});
    if (userName && !userId) {
        userId = await fetchUserIdByName({userName});
        if (IS_DEBUG) console.info("userId", userId);
    }

    const variables = {userID: userId};
    return fetchBase({
        variables,
        documentId: ENDPOINTS_DOCUMENT_ID.USER_REPLIES,
    });
};

export const fetchThreadReplies = ({threadId}) => {
    if (IS_DEBUG) console.info("=== fetchThreadReplies ===", {threadId});
    const variables = {postID: threadId};
    return fetchBase({
        variables,
        documentId: ENDPOINTS_DOCUMENT_ID.USER_PROFILE_THREADS_REPLIES,
    });
};

export const fetchPostReplies = ({threadId}) => {
    if (IS_DEBUG) console.info("=== fetchPostReplies ===", {threadId});
    const variables = {postID: threadId};
    return fetchBase({
        variables,
        documentId: ENDPOINTS_DOCUMENT_ID.THREADS_REPLIES,
    });
};
