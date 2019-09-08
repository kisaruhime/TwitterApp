package com.mazhara.utils.twitter;

import com.mazhara.utils.postre.PostgresUtils;
import twitter4j.*;
import twitter4j.conf.Configuration;
import twitter4j.conf.ConfigurationBuilder;
import java.sql.Connection;
import java.util.ArrayList;
import java.util.List;

public class TwitterUtils {


    private static List<String>  getCredentials() {

        final String ConsumerKey = System.getenv("CONSUMER_KEY");
        final String ConsumerSecret = System.getenv("CONSUMER_SECRET");
        final String AccessToken = System.getenv("ACCESS_TOKEN");
        final String AccessTokenSecret = System.getenv("ACCESS_TOKEN_SECRET");

        return new ArrayList() {{
            add(ConsumerKey);
            add(ConsumerSecret);
            add(AccessToken);
            add(AccessTokenSecret);
        }};

    }

    public static List<Long> getUsersFriendsIds(Twitter twitter, String user){

        List<Long> friends = new ArrayList<Long>();
        try {
            long cursor = -1;
            IDs ids;
            System.out.println("Listing followers's ids.");
            do {
                ids = twitter.getFriendsIDs(user, cursor);
                for (long id : ids.getIDs()) {
                    // System.out.println(friend.getName());
                    friends.add(id);
                }
            } while ((cursor = ids.getNextCursor()) != 0 && cursor < 25);
            System.out.println("Whole amount of friends :" + ids.getIDs().length);
        }catch (TwitterException e){
            e.printStackTrace();
        }catch (NullPointerException e){
            e.printStackTrace();
        }
        return friends;

    }

    public static List<String> getUsersFriends(Twitter twitter, String user){

        List<String> friends = new ArrayList<String>();
        try {
            long cursor = -1;
            IDs ids;
            System.out.println("Listing followers's ids.");
            do {
                ids = twitter.getFriendsIDs(user, cursor);
                for (long id : ids.getIDs()) {
                    User friend = twitter.showUser(id);
                   // System.out.println(friend.getName());
                    friends.add(friend.getName());
                }
            } while ((cursor = ids.getNextCursor()) != 0 && cursor < 25);
            System.out.println("Whole amount of friends :" + ids.getIDs().length);
        }catch (TwitterException e){
            e.printStackTrace();
        }catch (NullPointerException e){
            e.printStackTrace();
        }
        return friends;

    }

    public static Configuration getConfigs(){

        List<String> creds = getCredentials();
        ConfigurationBuilder cb = new ConfigurationBuilder();


        cb.setOAuthConsumerKey(creds.get(0));
        cb.setOAuthConsumerSecret(creds.get(1));
        cb.setOAuthAccessToken(creds.get(2));
        cb.setOAuthAccessTokenSecret(creds.get(3));

        cb.setJSONStoreEnabled(true);
        cb.setIncludeEntitiesEnabled(true);
        cb.setTweetModeExtended(true);
        return cb.build();
        //cb.setHttpStreamingReadTimeout(3_000_000);
    }

    public static Relationship getRelationship(Twitter twitter, String sourceUser, String targetUser){

        Relationship rel = null;
        try{
            rel = twitter.showFriendship(sourceUser,targetUser);
        }catch (TwitterException e){
            e.printStackTrace();
        }

        return rel;
    }

    public static void storeUserTweets(Twitter twitter, String user, int tweetsNum, Connection conn, String anotherUser){


        Paging page = new Paging(1, tweetsNum);
        ResponseList<Status> statuses;
        try {
            statuses = twitter.getUserTimeline(user, page);
            for (Status status : statuses) {
                if (status.getInReplyToScreenName() != null && status.getInReplyToScreenName().equals(anotherUser)) {
                    PostgresUtils.insertTweetsToTable(conn, status, user);
                    }
                }
        }catch (TwitterException e){
            e.printStackTrace();
        }

    }


}




