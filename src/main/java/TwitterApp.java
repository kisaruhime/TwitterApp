import twitter4j.Twitter;
import twitter4j.TwitterFactory;

import java.sql.Connection;
import java.util.List;


public class TwitterApp {

    public static void main(String[] args){

        Twitter twitter = new TwitterFactory(TwitterUtils.getConfigs()).getInstance();

        String user = System.getenv("TWITTER_USER");


        List<String> friends =  TwitterUtils.getUsersFriends(twitter,user);
        for (String friend: friends){
            TwitterUtils.getUserTweets(twitter, friend, 100, user);
        }
        String urlDB = System.getenv("POSTGRES_URL");
        String userDB = System.getenv("POSTGRES_USER");
        String passwordDB = System.getenv("POSTGRES_PASSWORD");
        Connection connection = PostgresUtils.connectToPostgres(urlDB, userDB, passwordDB);
        PostgresUtils.createTables(connection, user);


    }

}
