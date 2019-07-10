package com.mazhara.utils.prepocess;

public class TextUtils {

    public static String cleanText(String str){
        str = str.toLowerCase();
        str = str.replaceAll("[0-9]", "");
        str = str.replaceAll("http\\S+", "");
        str = str.replaceAll("www\\S+", "");
        str = str.replaceAll("rt", "");
        str = str.replaceAll("@\\w+", "");
        str = str.replaceAll("\\p{Punct}", "");
        return str;
    }

}
