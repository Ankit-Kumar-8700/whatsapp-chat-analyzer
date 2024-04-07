import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("Whatsapp Chat Analyzer")

def modifyAX():
    inColor='#090d12'
    outColor='#090d12'
    lining='gray'
    fig,ax = plt.subplots(facecolor=outColor)
    for axis in ['bottom', 'left']:
        ax.spines[axis].set_color(lining)
    for axis in ['top', 'right']:
        ax.spines[axis].set_color(inColor)
    ax.set_facecolor(inColor)
    return fig,ax

def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha = 'center', color='gray',
                 bbox = dict(facecolor = '#111111', alpha =.8, edgecolor='gray', boxstyle='round,pad=1'))

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)

    if st.sidebar.button("Show Analysis"):

        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,df)
        emoji_df = helper.emoji_helper(selected_user,df)
        st.title("Top Statistics")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)

        col1, col2 = st.columns(2)    
        with col1:
            st.header("Links Shared")
            st.title(num_links)
        with col2:
            st.header("Emojis Used")
            st.title(emoji_df[1].sum())

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user,df)
        fig,ax = modifyAX()
        plt.xticks(rotation='vertical',color='#a1a1a1')
        plt.yticks(color='#a1a1a1')
        ax.plot(timeline['time'], timeline['message'],color='green', marker='o', linestyle='-')
        for i, (xi, yi) in enumerate(zip(timeline['time'], timeline['message'])):
            plt.annotate(f'({xi}, {yi})', (xi, yi), textcoords="offset points", xytext=(0, 10), ha='center', color='#a1a1a1')
 
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = modifyAX()
        plt.xticks(rotation='vertical',color='#a1a1a1')
        plt.yticks(color='#a1a1a1')
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='#000040', marker='o', linestyle='-')
        for i, (xi, yi) in enumerate(zip(daily_timeline['only_date'], daily_timeline['message'])):
            plt.annotate(f'{yi}', (xi, yi), textcoords="offset points", xytext=(0, 10), ha='center', color='#a1a1a1')
 
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1,col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user,df)
            fig,ax = modifyAX()
            plt.xticks(rotation='vertical',color='#a1a1a1')
            plt.yticks(color='#a1a1a1')
            ax.bar(busy_day.index,busy_day.values,color='purple', edgecolor='gray', align='center')
            addlabels(busy_day.index,busy_day.values)
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = modifyAX()
            plt.xticks(rotation='vertical',color='#a1a1a1')
            plt.yticks(color='#a1a1a1')
            ax.bar(busy_month.index, busy_month.values,color='orange', edgecolor='gray', align='center')
            addlabels(busy_month.index, busy_month.values)
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user,df)
        fig,ax = modifyAX()
        plt.xticks(color='#a1a1a1')
        plt.yticks(color='#a1a1a1')
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x,new_df = helper.most_busy_users(df)
            fig, ax = modifyAX()
            plt.xticks(rotation='vertical',color='#a1a1a1')
            plt.yticks(color='#a1a1a1')

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='#000033', edgecolor='gray', align='center')
                addlabels(x.index, x.values)
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user,df)
        fig,ax = modifyAX()
        plt.xticks(color='#a1a1a1')
        plt.yticks(color='#a1a1a1')
        ax.imshow(df_wc)
        st.pyplot(fig)

        # most common words
        most_common_df = helper.most_common_words(selected_user,df)

        fig,ax = modifyAX()
        plt.xticks(rotation='vertical',color='#a1a1a1')
        plt.yticks(color='#a1a1a1')

        ax.barh(most_common_df[0],most_common_df[1], color='gray', edgecolor='white', align='center')
        st.title('Most commmon words')
        st.pyplot(fig)

        # emoji analysis
        st.title("Emoji Analysis")

        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig,ax = modifyAX()
            plt.xticks(color='#a1a1a1')
            plt.yticks(color='#a1a1a1')
            sz=len(emoji_df[0].head())
            myExplode=[0.03]*sz
            patches, texts, pcts =ax.pie(emoji_df[1].head(),labels=emoji_df[0].head(),autopct="%0.2f", explode=myExplode, shadow=True)
            for i, patch in enumerate(patches):
                texts[i].set_color(patch.get_facecolor())
            plt.setp(pcts, color='white')
            plt.setp(texts, fontweight=600)
            st.pyplot(fig)