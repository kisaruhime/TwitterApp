import twitter4j.*;
import twitter4j.conf.ConfigurationBuilder;
import twitter4j.json.DataObjectFactory;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

public class Main {

    static int pageno = 1;
    static final String fileName = "D:/big_data/homeworks/kafka_advanced/tweets.txt";
    public static void main(String[] args) {
        // gets Twitter instance with default credentials
//        ConfigurationBuilder cb = new ConfigurationBuilder();
//        cb.setOAuthConsumerKey(consumerKey);
//        cb.setOAuthConsumerSecret(consumerSecret);
//        cb.setOAuthAccessToken(accessToken);
//        cb.setOAuthAccessTokenSecret(accessTokenSecret);
//        cb.setJSONStoreEnabled(true);
//        cb.setIncludeEntitiesEnabled(true);
//        cb.setTweetModeExtended(true);
//        //cb.setHttpStreamingReadTimeout(3_000_000);
//
//        System.out.println("all args: " + consumerKey + " " + consumerSecret + " " + accessToken + " " + accessTokenSecret );
//
//        //call method ConfigurationBuilder that returns kafka producer obj
//
//        //creating TwitterStream obj
//        Twitter twitter = new TwitterFactory(cb.build()).getInstance();
//        try {
//
//            Paging page = new Paging(pageno++, 1000);
//            List<Status> statuses;
//
//            statuses = twitter.getUserTimeline(user, page);
//
//
//            System.out.println("Showing @" + user + "'s user timeline.");
//            for (Status status : statuses) {
//                System.out.println("@" + status.getUser().getScreenName() + " - " + status.getText());
//                try{
//                    FileWriter fw = new FileWriter(fileName, true);
//                    BufferedWriter bw = new BufferedWriter(fw);
//                    bw.write(DataObjectFactory.getRawJSON(status));
//                    bw.newLine();
//                    bw.close();
//                } catch(IOException exception){
//                    exception.printStackTrace();
//                }
//            }
//
//        } catch (TwitterException te) {
//            te.printStackTrace();
//            System.out.println("Failed to get timeline: " + te.getMessage());
//            System.exit(-1);
//        }

    }

}
