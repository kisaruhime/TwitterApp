package com.mazhara.utils.apps;
import com.mazhara.utils.postre.PostgresUtils;
import com.mazhara.utils.twitter.TwitterUtils;
import twitter4j.Twitter;
import twitter4j.TwitterFactory;
import java.sql.Connection;



public class TwitterApp {

    public static void main(String[] args){

        Twitter twitter = new TwitterFactory(TwitterUtils.getConfigs()).getInstance();


        String user1 = System.getenv("USER1");
        String user2 = System.getenv("USER2");

        System.out.println("User 1: "+user1);
        System.out.println("User 2: "+user2);

        Connection connection = PostgresUtils.connectToPostgres();

        PostgresUtils.createTable(connection, user1);
        PostgresUtils.createTable(connection, user2);

        TwitterUtils.storeUserTweets(twitter, user1, 1000, connection, user2);
        TwitterUtils.storeUserTweets(twitter, user2, 1000, connection, user1);


    }

}
