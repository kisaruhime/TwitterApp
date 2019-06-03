import org.apache.kafka.common.protocol.types.Field;
import twitter4j.*;
import twitter4j.conf.Configuration;
import twitter4j.conf.ConfigurationBuilder;

import java.util.ArrayList;
import java.util.Collections;
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


    public static List<String> getUsersFriends(Twitter twitter, String user){

        List<String> friends = null;
        try {
            long cursor = -1;
            IDs ids;
            System.out.println("Listing followers's ids.");
            do {
                ids = twitter.getFriendsIDs(user, cursor);
                for (long id : ids.getIDs()) {
                    User friend = twitter.showUser(id);
                    System.out.println(friend.getName());
                    friends.add(friend.getName());
                }
            } while ((cursor = ids.getNextCursor()) != 0);
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

    public static void getUserTweets(Twitter twitter, String user, int tweetsNum, String sourceUser){


        Paging page = new Paging(2, tweetsNum);
        List<Status> statuses;
        try {
            statuses = twitter.getUserTimeline(user, page);
            System.out.println("Showing @" + user + "'s user timeline.");
            for (Status status : statuses) {
                if (status.getInReplyToScreenName().equals(sourceUser)) {
                    System.out.println(status.getText());
                }
            }
        }catch (TwitterException e){
            e.printStackTrace();
        }

    }
}



